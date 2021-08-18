from django.forms import ModelForm

from dnevnik.models import Score


class ScoreAddForm(ModelForm):
    class Meta:
        model = Score
        fields = ('score',
                  'subject',
                  'comment',
                  )
