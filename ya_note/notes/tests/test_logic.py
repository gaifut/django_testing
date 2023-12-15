from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .shared_test_input import SharedTestInput
from .shared_urls import (
    NOTES_ADD_URL,
    NOTE_CREATE_SUCCESS,
    NOTES_DELETE_URL,
    NOTES_EDIT_URL,
)


User = get_user_model()

FORM_DATA_NOTE = {
    'title': 'Заметка 2',
    'text': 'Просто текст2',
    'slug': 'Zametka-2'
}

FORM_DATA_NO_SLUG = {
    'title': 'Заметка 1',
    'text': 'Просто текст',
    'slug': ''
}

FORM_DATA_DUPLICATE_SLUG = {
    'title': 'Заметка 1',
    'text': 'Просто текст',
    'slug': 'Zametka-1'
}


class TestNoteCreateEditDelete(SharedTestInput):

    def test_anonymous_user_cannot_create_note(self):
        self.generate_single_note()
        initial_notes_id = [note.id for note in Note.objects.all()]
        initial_notes_text = [note.text for note in Note.objects.all()]
        initial_notes_title = [note.title for note in Note.objects.all()]
        initial_notes_slug = [note.slug for note in Note.objects.all()]
        initial_note_count = Note.objects.count()
        self.client.post(NOTES_ADD_URL, data=FORM_DATA_NOTE)
        final_note_count = Note.objects.count()
        final_notes_id = [note.id for note in Note.objects.all()]
        final_notes_text = [note.text for note in Note.objects.all()]
        final_notes_title = [note.title for note in Note.objects.all()]
        final_notes_slug = [note.slug for note in Note.objects.all()]
        self.assertEqual(initial_note_count, final_note_count)
        self.assertEqual(initial_notes_id, final_notes_id)
        self.assertEqual(initial_notes_text, final_notes_text)
        self.assertEqual(initial_notes_title, final_notes_title)
        self.assertEqual(initial_notes_slug, final_notes_slug)

    def test_user_can_create_note(self):
        initial_note_count = Note.objects.count()
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL, data=FORM_DATA_NOTE), NOTE_CREATE_SUCCESS
        )
        note_last = Note.objects.last()
        self.assertEqual(initial_note_count + 1, Note.objects.count())
        self.assertEqual(note_last.title, FORM_DATA_NOTE['title'])
        self.assertEqual(note_last.text, FORM_DATA_NOTE['text'])
        self.assertEqual(note_last.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(note_last.author, self.user_author)

        unchanged_notes = Note.objects.exclude(id=note_last.id)
        for note in unchanged_notes:
            self.assertEqual(note.title, f"Заметка {note}")
            self.assertEqual(note.text, "Просто текст")
        self.assertEqual(initial_note_count + 1, Note.objects.count())

    def test_author_can_delete_note(self):
        self.generate_single_note()
        initial_note_count = Note.objects.count()
        self.client_author.delete(NOTES_DELETE_URL)
        final_note_count = Note.objects.count()
        self.assertEqual(initial_note_count - 1, final_note_count)
        remaining_notes = Note.objects.filter(
            id__in=[note.id for note in Note.objects.all()])
        for note in remaining_notes:
            self.assertEqual(note.title, f"Заметка {note}")
            self.assertEqual(note.text, "Просто текст")
        self.assertEqual(initial_note_count - 1, Note.objects.count())

    def test_user_cant_delete_note_of_another_user(self):
        self.generate_single_note()
        self.client_another.delete(NOTES_DELETE_URL)
        self.assertNotEqual(
            self.client_another.delete(
                NOTES_DELETE_URL).status_code, HTTPStatus.NO_CONTENT
        )
        deleted_note = Note.objects.filter(id=self.note.id).first()
        self.assertIsNotNone(deleted_note)
        self.assertEqual(deleted_note.title, self.note.title)
        self.assertEqual(deleted_note.text, self.note.text)
        self.assertEqual(deleted_note.slug, self.note.slug)
        self.assertEqual(deleted_note.author, self.user_author)

    def test_author_can_edit_note(self):
        self.generate_single_note()
        self.assertIn(
            self.client_author.post(
                NOTES_EDIT_URL, data=FORM_DATA_NOTE
            ).status_code, (HTTPStatus.OK, HTTPStatus.FOUND)
        )
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(updated_note.text, FORM_DATA_NOTE['text'])
        self.assertEqual(updated_note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(updated_note.author, self.user_author)

    def test_user_cant_edit_note_of_another_user(self):
        self.generate_single_note()
        self.assertEqual(self.client_another.post(
            NOTES_EDIT_URL, data=FORM_DATA_NOTE
        ).status_code, HTTPStatus.NOT_FOUND)
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.author, self.user_author)

    def test_cannot_create_note_with_duplicate_slug(self):
        self.generate_single_note()
        response = self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_DUPLICATE_SLUG
        )
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)
        self.assertIn(WARNING, response.content.decode())

    def test_user_can_create_note_without_slug(self):
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_NO_SLUG
        ), NOTE_CREATE_SUCCESS)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get(
            title=FORM_DATA_NO_SLUG['title'],
            author=self.user_author,
            text=FORM_DATA_NO_SLUG['text'],
            slug=slugify(FORM_DATA_NO_SLUG['title'])
        )
        self.assertEqual(created_note.title, FORM_DATA_NO_SLUG['title'])
        self.assertEqual(created_note.text, FORM_DATA_NO_SLUG['text'])
        self.assertEqual(created_note.slug, slugify(
            FORM_DATA_NO_SLUG['title']
        ))
        self.assertEqual(created_note.author, self.user_author)
