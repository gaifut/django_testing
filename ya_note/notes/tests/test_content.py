from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class Notelistpage(TestCase):
    NOTE_LIST_URL = reverse('notes:list')

    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create(username='user author')
        cls.user_another = User.objects.create(username='user another')
        all_notes = []
        for index in range(2):
            note = Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=cls.user_author
            )
            note.slug = f'note-{index}'
            all_notes.append(note)
        Note.objects.bulk_create(all_notes)

        note_another_user = Note(
            title=f'Заметка another user {index}',
            text='Просто текст.',
            author=cls.user_another
        )
        note_another_user.slug = f'note-{index}'

    def test_notes_list_display_and_order(self):
        self.client.force_login(self.user_author)
        response = self.client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']
        all_ids = [note.id for note in object_list]
        sorted_ids = sorted(all_ids)
        self.assertEqual(all_ids, sorted_ids)
        note_one = Note.objects.get(title='Заметка 1')
        self.assertIn(note_one, object_list)

    def test_notes_of_different_users_dont_intersect(self):
        self.client.force_login(self.user_author)
        response = self.client.get(self.NOTE_LIST_URL)
        object_list = response.context['object_list']

        for note in object_list:
            with self.subTest(note=note):
                self.assertEqual(note.author, self.user_author)

    def test_create_note_page_displays_form(self):
        self.client.force_login(self.user_author)
        response = self.client.get(reverse('notes:add'))
        form = response.context['form']
        self.assertIsNotNone(form)

    def test_edit_note_page_displays_form(self):
        note_to_edit = Note.objects.first()
        self.client.force_login(self.user_author)
        response = self.client.get(
            reverse('notes:edit', args=(note_to_edit.slug,))
        )
        form = response.context['form']
        self.assertIsNotNone(form)
