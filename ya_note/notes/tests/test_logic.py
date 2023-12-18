from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.models import Note
from .shared_test_input import SharedTestInput
from .shared_urls import (
    NOTES_ADD_URL,
    NOTE_CREATE_SUCCESS_URL,
    NOTES_DELETE_URL,
    NOTES_EDIT_URL,
    SLUG,
)


User = get_user_model()

FORM_DATA_NOTE = {
    'title': 'Заметка 2',
    'text': 'Просто текст2',
    'slug': 'Zametka-2'
}

FORM_DATA_NO_SLUG = {
    'title': 'Заметка 3',
    'text': 'Просто текст',
    'slug': ''
}

FORM_DATA_DUPLICATE_SLUG = {
    'title': 'Заметка 1',
    'text': 'Просто текст',
    'slug': 'Zametka-1'
}


class TestNoteCreateEditDelete(SharedTestInput):
    generate_single_note = True

    def test_anonymous_user_cannot_create_note(self):
        initial_notes = set(Note.objects.all())
        initial_note_count = Note.objects.count()
        self.client.post(NOTES_ADD_URL, data=FORM_DATA_NOTE)
        self.assertEqual(initial_note_count, Note.objects.count())
        self.assertEqual(initial_notes, set(Note.objects.all()))

    def test_user_can_create_note(self):
        notes_inital = set(Note.objects.all())
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL, data=FORM_DATA_NOTE), NOTE_CREATE_SUCCESS_URL
        )
        notes_final = set(Note.objects.all())
        difference = notes_final - notes_inital
        self.assertEqual(len(difference), 1)
        new_note = difference.pop()
        self.assertEqual(new_note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(new_note.author, self.user_author)
        self.assertEqual(new_note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(new_note.text, FORM_DATA_NOTE['text'])

    def test_author_can_delete_note(self):
        initial_notes_count = Note.objects.count()
        self.client_author.delete(NOTES_DELETE_URL)
        final_notes_count = Note.objects.count()
        self.assertEqual(initial_notes_count, final_notes_count + 1)
        self.assertNotIn(Note.objects.filter(slug=SLUG), Note.objects.all())

    def test_user_cant_delete_note_of_another_user(self):
        note_to_delete_before_delete_attempt = Note.objects.get(slug=SLUG)
        self.assertNotEqual(
            self.client_another.delete(
                NOTES_DELETE_URL).status_code, HTTPStatus.NO_CONTENT
        )
        note_to_delete_after_delete_attempt = Note.objects.get(slug=SLUG)

        self.assertEqual(
            note_to_delete_before_delete_attempt.author,
            note_to_delete_after_delete_attempt.author
        )
        self.assertEqual(
            note_to_delete_before_delete_attempt.title,
            note_to_delete_after_delete_attempt.title
        )
        self.assertEqual(
            note_to_delete_before_delete_attempt.text,
            note_to_delete_after_delete_attempt.text
        )
        self.assertEqual(
            note_to_delete_before_delete_attempt.slug,
            note_to_delete_after_delete_attempt.slug
        )

    def test_author_can_edit_note(self):
        original_note = Note.objects.get(slug=SLUG)
        self.assertEqual(
            self.client_author.post(
                NOTES_EDIT_URL, data=FORM_DATA_NOTE
            ).status_code, HTTPStatus.FOUND
        )
        updated_note = Note.objects.get(id=self.note.id)
        self.assertEqual(updated_note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(updated_note.text, FORM_DATA_NOTE['text'])
        self.assertEqual(updated_note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(updated_note.author, original_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        initial_note = Note.objects.get(slug=SLUG)
        self.assertEqual(self.client_another.post(
            NOTES_EDIT_URL, data=FORM_DATA_NOTE
        ).status_code, HTTPStatus.NOT_FOUND)
        final_note = Note.objects.get(id=self.note.id)
        self.assertEqual(initial_note.author, final_note.author)
        self.assertEqual(initial_note.title, final_note.title)
        self.assertEqual(initial_note.text, final_note.text)
        self.assertEqual(initial_note.slug, final_note.slug)

    def test_cannot_create_note_with_duplicate_slug(self):
        initial_notes = set(Note.objects.all())
        self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_DUPLICATE_SLUG
        )
        final_notes = set(Note.objects.all())
        self.assertEqual(final_notes, initial_notes)

    def test_user_can_create_note_without_slug(self):
        initial_notes = set(Note.objects.all())
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_NO_SLUG
        ), NOTE_CREATE_SUCCESS_URL)
        final_notes = set(Note.objects.all())
        difference = final_notes.difference(initial_notes)
        self.assertEqual(len(difference), 1)
        created_note = difference.pop()
        self.assertEqual(created_note.title, FORM_DATA_NO_SLUG['title'])
        self.assertEqual(created_note.text, FORM_DATA_NO_SLUG['text'])
        self.assertEqual(created_note.slug, slugify(
            FORM_DATA_NO_SLUG['title']
        ))
        self.assertEqual(created_note.author, self.user_author)
