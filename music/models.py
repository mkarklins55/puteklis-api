from django.db import models

from .storage import OverwriteStorage


class Song(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_CHOICES = [
        (STATUS_DRAFT, 'Draft'),
        (STATUS_PUBLISHED, 'Published'),
    ]

    title = models.CharField('Nosaukums', max_length=200)
    audio_file = models.FileField(
        'Audio fails',
        upload_to='music/',
        storage=OverwriteStorage(),
    )
    lyrics_file = models.FileField(
        'Teksta fails',
        upload_to='lyrics/',
        storage=OverwriteStorage(),
        blank=True,
    )
    cover_image = models.ImageField(
        'Vāka attēls',
        upload_to='cover/',
        storage=OverwriteStorage(),
    )
    style = models.TextField('Stils', blank=True)
    status = models.CharField(
        'Statuss',
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
    )
    published_at = models.DateField('Publicēts', blank=True, null=True)
    created_at = models.DateTimeField('Izveidots', blank=True, null=True)
    updated_at = models.DateTimeField('Atjaunināts', auto_now=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'audio_file'],
                name='unique_song_title_audio',
            ),
        ]
        verbose_name = 'Dziesma'
        verbose_name_plural = 'Dziesmas'

    def __str__(self) -> str:
        return self.title
