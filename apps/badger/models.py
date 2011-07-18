from django.db import models
from django.contrib.auth.models import User

from django.template.defaultfilters import slugify


def get_permissions_for(self, user):
    """Mixin method to collect permissions for a model instance""" 
    pre, suf = 'allows_', '_by'
    pre_len, suf_len = len(pre), len(suf)
    methods = (
        m for m in dir(self)
        if m.startswith(pre) and m.endswith(suf)
    )
    perms = dict(
        ( m[pre_len:0-suf_len], getattr(self, m)(user) )
        for m in methods
    )
    return perms


class BadgeManager(models.Manager):
    """Manager for Badge model objects"""
    pass


class Badge(models.Model):
    """Representation of a badge"""
    objects = BadgeManager()

    title = models.CharField(max_length=255, blank=False, unique=True)
    slug = models.SlugField(blank=False, unique=True)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, blank=False)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    class Meta:
        unique_together = ('title','slug')

    get_permissions_for = get_permissions_for

    def save(self, **kwargs):
        """Save the submission, updating slug and screenshot thumbnails"""
        if not self.slug:
            self.slug = slugify(self.title)
        super(Badge,self).save(**kwargs)

    def award_to(self, awarder, awardee, nomination=None):
        award = Award(user=awardee, badge=self, creator=awarder,
                nomination=nomination)
        award.save()
        return award

    def is_awarded_to(self, user):
        return Award.objects.filter(user=user, badge=self).count() > 0

    def nominate_for(self, nominator, nominee):
        nomination = Nomination(badge=self, creator=nominator, nominee=nominee)
        nomination.save()
        return nomination

    def is_nominated_for(self, user):
        return Nomination.objects.filter(nominee=user, badge=self).count() > 0


class NominationManager(models.Manager):
    pass


class NominationException(Exception): 
    pass


class NominationApproveNotAllowedException(NominationException): 
    pass


class NominationAcceptNotAllowedException(NominationException): 
    pass


class Nomination(models.Model):
    """Representation of a user nominated by another user for a badge"""
    objects = NominationManager()

    badge = models.ForeignKey(Badge)
    nominee = models.ForeignKey(User, related_name="nomination_nominee",
            blank=False, null=False)
    accepted = models.BooleanField(default=False)
    creator = models.ForeignKey(User, related_name="nomination_creator",
            blank=False, null=False)
    approver = models.ForeignKey(User, related_name="nomination_approver",
            blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    get_permissions_for = get_permissions_for

    def allows_approve_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.badge.creator: 
            return True
        return False

    def approve_by(self, approver):
        """Approve this nomination.
        Also awards, if already accepted."""
        if not self.allows_approve_by(approver):
            raise NominationApproveNotAllowedException()
        self.approver = approver
        self.save()
        self._award_if_ready()

    def is_approved(self):
        """Has this nomination been approved?"""
        return self.approver is not None

    def allows_accept_by(self, user):
        if user.is_staff or user.is_superuser:
            return True
        if user == self.nominee: 
            return True
        return False

    def accept(self, user):
        """Accept this nomination for the nominee.
        Also awards, if already approved."""
        if not self.allows_accept_by(user):
            raise NominationAcceptNotAllowedException()
        self.accepted = True
        self.save()
        self._award_if_ready()

    def is_accepted(self):
        """Has this nomination been accepted?"""
        return self.accepted

    def _award_if_ready(self):
        """If approved and accepted, award the badge to nominee on behalf of
        approver."""
        if self.is_approved() and self.is_accepted():
            self.badge.award_to(self.approver, self.nominee, self)


class AwardManager(models.Manager):
    pass


class Award(models.Model):
    """Representation of a badge awarded to a user"""
    objects = AwardManager()

    badge = models.ForeignKey(Badge)
    user = models.ForeignKey(User, related_name="award_user")
    nomination = models.ForeignKey(Nomination, blank=True, null=True)
    creator = models.ForeignKey(User, related_name="award_creator")
    created = models.DateTimeField(auto_now_add=True, blank=False)
    modified = models.DateTimeField(auto_now=True, blank=False)

    get_permissions_for = get_permissions_for
