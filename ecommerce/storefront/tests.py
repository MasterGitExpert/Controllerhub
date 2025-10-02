from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage
from .forms import ContactForm

class ContactFormTestCase(TestCase):
    """Unit tests for the contact form functionality"""
    
    def setUp(self):
        """Set up test client and URLs"""
        self.client = Client()
        self.contact_url = reverse('contact')
    
    def test_contact_page_loads(self):
        """Test that the contact page loads successfully"""
        response = self.client.get(self.contact_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact.html')
    
    def test_contact_form_displays(self):
        """Test that the contact form is present on the page"""
        response = self.client.get(self.contact_url)
        self.assertContains(response, '<form')
        self.assertContains(response, 'name="name"')
        self.assertContains(response, 'name="email"')
        self.assertContains(response, 'name="subject"')
        self.assertContains(response, 'name="message"')
    
    def test_valid_contact_form_submission(self):
        """Test submitting a valid contact form"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with more than 10 characters.'
        }
        response = self.client.post(self.contact_url, data=form_data)
        
        # Check that the message was saved
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        # Check the saved message details
        message = ContactMessage.objects.first()
        self.assertEqual(message.name, 'Test User')
        self.assertEqual(message.email, 'test@example.com')
        self.assertEqual(message.subject, 'Test Subject')
        self.assertIn('test message', message.message)
        self.assertFalse(message.is_read)
        
        # Check redirect after successful submission
        self.assertEqual(response.status_code, 302)
    
    def test_invalid_email_format(self):
        """Test form validation with invalid email"""
        form_data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_message_too_short(self):
        """Test form validation with message shorter than 10 characters"""
        form_data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Short'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
    
    def test_missing_required_fields(self):
        """Test form validation with missing required fields"""
        # Missing name
        form_data = {
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.'
        }
        form = ContactForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_contact_message_string_representation(self):
        """Test the string representation of ContactMessage model"""
        message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message content.'
        )
        self.assertEqual(str(message), 'Test User - Test Subject')
    
    def test_contact_message_ordering(self):
        """Test that contact messages are ordered by creation date (newest first)"""
        # Create multiple messages
        ContactMessage.objects.create(
            name='User 1',
            email='user1@example.com',
            subject='First Message',
            message='First message content.'
        )
        ContactMessage.objects.create(
            name='User 2',
            email='user2@example.com',
            subject='Second Message',
            message='Second message content.'
        )
        
        messages = ContactMessage.objects.all()
        self.assertEqual(messages[0].subject, 'Second Message')
        self.assertEqual(messages[1].subject, 'First Message')
    
    def test_mark_as_read_functionality(self):
        """Test marking a contact message as read"""
        message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message content.'
        )
        
        # Initially should be unread
        self.assertFalse(message.is_read)
        
        # Mark as read
        message.is_read = True
        message.save()
        
        # Verify it's marked as read
        updated_message = ContactMessage.objects.get(id=message.id)
        self.assertTrue(updated_message.is_read)


class ContactFormFieldTestCase(TestCase):
    """Test individual form field validations"""
    
    def test_form_field_labels(self):
        """Test that form fields have correct widgets"""
        form = ContactForm()
        self.assertEqual(
            form.fields['name'].widget.attrs['placeholder'],
            'Your Name'
        )
        self.assertEqual(
            form.fields['email'].widget.attrs['placeholder'],
            'your.email@example.com'
        )
    
    def test_form_field_css_classes(self):
        """Test that form fields have correct CSS classes"""
        form = ContactForm()
        self.assertEqual(
            form.fields['name'].widget.attrs['class'],
            'form-input'
        )
        self.assertEqual(
            form.fields['message'].widget.attrs['class'],
            'form-textarea'
        )