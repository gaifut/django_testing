from http import HTTPStatus

from django.contrib.auth import get_user_model
from pytils.translit import slugify

from notes.forms import WARNING
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
        self.assertSetEqual(initial_notes, set(Note.objects.all()))

    def test_user_can_create_note(self):
        objects_before_inquiry = set(Note.objects.all())
        self.assertRedirects(self.client_author.post(
            NOTES_ADD_URL, data=FORM_DATA_NOTE), NOTE_CREATE_SUCCESS_URL
        )
        objects_after_inquiry = set(Note.objects.all())
        difference = objects_after_inquiry.difference(objects_before_inquiry)
        self.assertEqual(len(difference), 1)
        new_note = difference.pop()
        self.assertEqual(new_note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(new_note.author, self.user_author)
        self.assertEqual(new_note.slug, FORM_DATA_NOTE['slug'])
        self.assertEqual(new_note.text, FORM_DATA_NOTE['text'])

    def test_author_can_delete_note(self):
        initial_notes = set(Note.objects.all())
        self.client_author.delete(NOTES_DELETE_URL)
        final_notes = set(Note.objects.all())
        difference = initial_notes.difference(final_notes)
        self.assertEqual(len(difference), 1)
        self.assertEqual(difference.pop().slug, SLUG)

    def test_user_cant_delete_note_of_another_user(self):
        initial_notes = set(Note.objects.all())
        self.assertNotEqual(
            self.client_another.delete(
                NOTES_DELETE_URL).status_code, HTTPStatus.NO_CONTENT
        )
        final_notes = set(Note.objects.all())
        difference = initial_notes.difference(final_notes)
        self.assertEqual(len(difference), 0)
        note_to_delete_initial_set = next(
            note for note in initial_notes if note.slug == SLUG
        )
        note_to_delete_after_delete_attempt = next(
            note for note in final_notes if note.slug == SLUG
        )
        self.assertEqual(
            note_to_delete_initial_set.author,
            note_to_delete_after_delete_attempt.author
        )

        self.assertEqual(
            note_to_delete_initial_set.title,
            note_to_delete_after_delete_attempt.title
        )
        self.assertEqual(
            note_to_delete_initial_set.text,
            note_to_delete_after_delete_attempt.text
        )

    def test_author_can_edit_note(self):
        initial_notes = set(Note.objects.all())
        self.assertEqual(
            self.client_author.post(
                NOTES_EDIT_URL, data=FORM_DATA_NOTE
            ).status_code, HTTPStatus.FOUND
        )
        updated_note = Note.objects.get(id=self.note.id)
        original_note = next(
            note for note in initial_notes if note.slug == SLUG
        )
        self.assertEqual(updated_note.title, FORM_DATA_NOTE['title'])
        self.assertEqual(updated_note.text, FORM_DATA_NOTE['text'])
        self.assertEqual(updated_note.author, original_note.author)

    def test_user_cant_edit_note_of_another_user(self):
        initial_notes = set(Note.objects.all())
        self.assertEqual(self.client_another.post(
            NOTES_EDIT_URL, data=FORM_DATA_NOTE
        ).status_code, HTTPStatus.NOT_FOUND)
        final_notes = set(Note.objects.all())
        difference = initial_notes.difference(final_notes)
        self.assertEqual(len(difference), 0)
        note_to_edit_initial_set = next(
            note for note in initial_notes if note.slug == SLUG
        )
        note_to_edit_after_edit_attempt = next(
            note for note in final_notes if note.slug == SLUG
        )

        self.assertEqual(
            note_to_edit_initial_set.author,
            note_to_edit_after_edit_attempt.author
        )

        self.assertEqual(
            note_to_edit_initial_set.title,
            note_to_edit_after_edit_attempt.title
        )
        self.assertEqual(
            note_to_edit_initial_set.text,
            note_to_edit_after_edit_attempt.text
        )

    def test_cannot_create_note_with_duplicate_slug(self):
        initial_notes = set(Note.objects.all())
        response = self.client_author.post(
            NOTES_ADD_URL,
            data=FORM_DATA_DUPLICATE_SLUG
        )
        self.assertNotEqual(response.status_code, HTTPStatus.FOUND)
        self.assertIn(WARNING, response.content.decode())
        final_notes = set(Note.objects.all())
        difference = initial_notes.difference(final_notes)
        self.assertEqual(len(difference), 0)
        note_to_edit_initial_set = next(
            note for note in initial_notes if note.slug == SLUG
        )
        note_to_edit_after_edit_attempt = next(
            note for note in final_notes if note.slug == SLUG
        )
        self.assertEqual(
            note_to_edit_initial_set.author,
            note_to_edit_after_edit_attempt.author
        )

        self.assertEqual(
            note_to_edit_initial_set.title,
            note_to_edit_after_edit_attempt.title
        )
        self.assertEqual(
            note_to_edit_initial_set.text,
            note_to_edit_after_edit_attempt.text
        )

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
