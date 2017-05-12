"""Notifications module"""

from pushbullet import Pushbullet
from mailthon import postman, email

import settings


def translate_station(code):
    """Translate station name from code"""
    if code == settings.FROM_STATION_CODE:
        return settings.FROM_STATION_LABEL
    elif code == settings.TO_STATION_CODE:
        return settings.TO_STATION_LABEL
    else:
        raise Exception('Unknown station code %s' % code)


def send(data, cancel=False):
    """Send notifications"""

    if settings.MAIL_ENABLED:
        send_mail(data, cancel=cancel)

    if settings.PUSHBULLET_ENABLED:
        send_push(data, cancel=cancel)


def send_mail(data, cancel=False):
    """Send an email"""
    body = "Le train de %s (%s - %s) a été %s." % (
        data['date'],
        translate_station(data['from_gare']),
        translate_station(data['to_gare']),
        u'supprimé' if not cancel else u'remis en service'
    )

    the_email = email(
        subject='%sSuppression Transilien' % (u'[ANNULATION] ' if cancel else ''),
        content=body,
        sender=settings.MAIL_DEFAULT_SENDER,
        receivers=settings.MAIL_RECIPIENTS
    )

    if not settings.TESTING:
        smtp = postman(host=settings.MAIL_SERVER, port=settings.MAIL_PORT)
        smtp.send(the_email)


def send_push(data, cancel=False):
    """Send a message through Pushbullet"""
    title = u'%s%s %s > %s' % (
        u'[ANNULATION] ' if cancel else '',
        data['date'],
        translate_station(data['from_gare']),
        translate_station(data['to_gare'])
    )
    body = u'Le train de %s (%s - %s) a été %s.' % (
        data['date'],
        translate_station(data['from_gare']),
        translate_station(data['to_gare']),
        u'supprimé' if not cancel else u'remis en service'
    )
    if not settings.TESTING:
        pushb = Pushbullet(settings.PUSHBULLET_API_KEY)
        channel = pushb.get_channel(settings.PUSHBULLET_CHANNEL)
        channel.push_note(title, body)
