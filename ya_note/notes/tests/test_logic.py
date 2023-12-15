from django.contrib.auth import get_user_model
from http import HTTPStatus
from pytils.translit import slugify

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
        initial_note_count = Note.objects.count()
        self.client.post(NOTES_ADD_URL, data=FORM_DATA_NOTE)
        final_note_count = Note.objects.count()
        self.assertEqual(initial_note_count, final_note_count)

    def test_user_can_create_note(self):
        initial_note_count = Note.objects.count()
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL, data=FORM_DATA_NOTE), NOTE_CREATE_SUCCESS
        )
        final_note_count = Note.objects.count()
        self.assertEqual(initial_note_count + 1, final_note_count)
        self.assertEqual(Note.objects.last().title, FORM_DATA_NOTE['title'])
        self.assertEqual(Note.objects.last().text, FORM_DATA_NOTE['text'])
        self.assertEqual(Note.objects.last().slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(Note.objects.last().author, self.user_author)

    def test_author_can_delete_note(self):
        self.generate_single_note()
        initial_note_count = Note.objects.count()
        self.client_author.delete(NOTES_DELETE_URL)
        final_note_count = Note.objects.count()
        self.assertEqual(initial_note_count - 1, final_note_count)

    def test_user_cant_delete_note_of_another_user(self):
        self.generate_single_note()
        initial_notes = list(Note.objects.all())
        self.client_another.delete(NOTES_DELETE_URL)
        self.assertNotEqual(
            self.client_another.delete(
                NOTES_DELETE_URL).status_code, HTTPStatus.NO_CONTENT
        )
        final_notes = list(Note.objects.all())
        self.assertListEqual(initial_notes, final_notes)
        self.assertEqual(Note.objects.first().title, self.note.title)
        self.assertEqual(Note.objects.first().text, self.note.text)
        self.assertEqual(Note.objects.first().slug, self.note.slug)

    def test_author_can_edit_note(self):
        self.generate_single_note()
        self.client_author.post(NOTES_EDIT_URL, data=FORM_DATA_NOTE)
        self.note.refresh_from_db()
        self.assertEqual(self.note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(self.note.text, FORM_DATA_NOTE['text'])
        self.assertEqual(self.note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(self.note.author, self.user_author)

    def test_user_cant_edit_note_of_another_user(self):
        self.generate_single_note()
        response = self.client_another.post(
            NOTES_EDIT_URL, data=FORM_DATA_NOTE
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertNotEqual(self.note.title, FORM_DATA_NOTE['title'])
        self.assertNotEqual(self.note.text, FORM_DATA_NOTE['text'])
        self.assertNotEqual(self.note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(self.note.author, self.user_author)

    def test_cannot_create_note_with_duplicate_slug(self):
        self.generate_single_note()
        response = self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_DUPLICATE_SLUG
        )
        self.assertNotEqual(
            response.status_code,
            HTTPStatus.FOUND,
        )
        note_count = Note.objects.count()
        self.assertEqual(note_count, 1)

    def test_user_can_create_note_without_slug(self):
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_NO_SLUG
        ), NOTE_CREATE_SUCCESS)
        self.assertEqual(Note.objects.count(), 1)
        created_note = Note.objects.get(
            title=FORM_DATA_NO_SLUG['title']
        )
        self.assertEqual(created_note.title, FORM_DATA_NO_SLUG['title'])
        self.assertEqual(created_note.text, FORM_DATA_NO_SLUG['text'])
        self.assertEqual(created_note.slug, slugify(
            FORM_DATA_NO_SLUG['title']
        ))
        self.assertEqual(created_note.author, self.user_author)
