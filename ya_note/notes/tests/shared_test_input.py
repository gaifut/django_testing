from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from notes.models import Note

User = get_user_model()


class SharedTestInput(TestCase):
    generate_note_list_author = False
    generate_single_note = False

    @classmethod
    def setUpTestData(cls):
        cls.user_author = User.objects.create(username='author')
        cls.client_author = Client()
        cls.client_author.force_login(cls.user_author)
        cls.user_another = User.objects.create(username='another')
        cls.client_another = Client()
        cls.client_another.force_login(cls.user_another)

        if cls.generate_single_note is True:
            cls.note = Note.objects.create(
                title='Заметка 1',
                text='Просто текст',
                author=cls.user_author,
                slug='Zametka-1'
            )

        if cls.generate_note_list_author is True:
            Note.objects.bulk_create(
                Note(
                    title=f'Заметка {index}',
                    text='Просто текст.',
                    author=cls.user_author,
                    slug=f'Zametka-{index}'
                )for index in range(11)
            )
