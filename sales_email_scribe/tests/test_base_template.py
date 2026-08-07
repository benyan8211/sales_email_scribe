from django.test import SimpleTestCase
from django.template import Context, Template

class BaseTemplateDirectUnitTest(SimpleTestCase):
    def test_base_html_renders_directly_user_not_authenticated(self):
        """Test render of base.html with user not authenticated."""

        template_to_render = """
            {% extends "base.html" %}
            {% block content %}<p>Testing.</p>{% endblock %}
        """
        compiled_template = Template(template_to_render)
        
        context = Context({'user': {'is_authenticated': False}})
        rendered_html = compiled_template.render(context)
        
        self.assertIn('<a href="/accounts/login/">Log in here</a>', rendered_html)
        self.assertIn('/static/images/sales_email_scribe_logo.png', rendered_html)
        self.assertIn('<p>Testing.</p>', rendered_html)

    def test_base_html_renders_directly_user_is_authenticated(self):
        """Test render of base.html with user not authenticated."""

        template_to_render = """
            {% extends "base.html" %}
            {% block content %}<p>Testing.</p>{% endblock %}
        """
        compiled_template = Template(template_to_render)
        
        # Keep the context clear of complex objects to avoid DB queries
        context = Context({'user': {'is_authenticated': True, 'email': 'benyan@gmail.com'}})
        rendered_html = compiled_template.render(context)
        
        self.assertIn('Logged in as: benyan@gmail.com', rendered_html)
        self.assertIn(' <a href="#" onclick="this.closest(\'form\').submit(); return false;">Log out</a>', rendered_html)
        self.assertIn('/static/images/sales_email_scribe_logo.png', rendered_html)
        self.assertIn('<p>Testing.</p>', rendered_html)