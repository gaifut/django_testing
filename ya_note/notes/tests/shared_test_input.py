from django.contrib.auth import get_user_model
from notes.models import Note
from django.test import Client
User = get_user_model()


class SharedTestInputMixin():
    @classmethod
    def setUpTestData(cls, a=True, b=False):
        cls.user_author = User.objects.create(username='author')
        cls.user_another = User.objects.create(username='another')
        cls.client_another = Client()

    @classmethod
    def generate_single_note(cls):
        cls.note = Note.objects.create(
            title='Заметка 1',
            text='Просто текст',
            author=cls.user_author,
            slug='Zametka-1'
        )

    @classmethod
    def generate_note_list_author(cls, num_notes=11):
        all_notes = [
            Note(
                title=f'Заметка {index}',
                text='Просто текст.',
                author=cls.user_author,
                slug=f'Zametka-{index}'
            )
            for index in range(num_notes)
        ]
        Note.objects.bulk_create(all_notes)

    @classmethod
    def login_author(cls):
        cls.client_author = Client()
        cls.client_author.force_login(cls.user_author)

    @classmethod
    def login_another(cls):
        cls.client_another = Client()
        cls.client_another.force_login(cls.user_another)
