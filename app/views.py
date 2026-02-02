from django.shortcuts import render

# Create your views here.

class SettingUpdateView(UpdateView):
    model = User
    fields = ['is_advice']
    template_name = 'setting_update.html'

    def get_object(self):
        return self.request.user
