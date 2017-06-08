# -*- encoding: utf-8 -*-

__author__ = 'kotaimen'
__date__ = '04/01/2017'

"""Print stack events"""

import time
import click
import boto3
import botocore.exceptions
import threading

from ..utils import STACK_STATUS_TO_COLOR


def tail_stack_events(session,
                      stack,
                      latest_events=5,
                      event_limit=10000,
                      time_limit=3600,
                      check_interval=5,
                      indent=0,
                      prefix='XX'):
    """Tail stack events and print them"""
    then = time.time()

    visited_events = set()

    visited_stacks = set()
    visited_stacks.add(stack.stack_id)

    first_run = True

    # loop until time limit
    while time.time() - then < time_limit:
        # or too many events are visited
        if len(visited_events) > event_limit:
            break

        # get all stack events
        try:
            events = list(stack.events.all())
        except botocore.exceptions.ClientError as e:
            click.echo(str(e))
            break
        else:
            # put latest events at first
            events.reverse()
            event_count = len(events)

        # https://boto3.readthedocs.io/en/latest/reference/services/cloudformation.html#event
        for n, e in enumerate(events):
            # skip visited events
            if e.event_id in visited_events:
                continue
            else:
                visited_events.add(e.event_id)

            # tail only latest events
            if first_run:
                if latest_events > 0:
                    if n < event_count - latest_events:
                        continue

            # tail sub stack events
            if e.resource_type == 'AWS::CloudFormation::Stack' and \
                    e.physical_resource_id and \
                            e.physical_resource_id not in visited_stacks:
                visited_stacks.add(e.physical_resource_id)

                cfn = session.resource('cloudformation',
                                       region_name=stack.meta.client.meta.region_name)
                sub_stack = cfn.Stack(e.physical_resource_id)

                start_tail_stack_events_daemon(session,
                                               sub_stack,
                                               latest_events=latest_events,
                                               check_interval=check_interval,
                                               indent=indent + 2,
                                               prefix=e.logical_resource_id)
            # print the event
            if indent > 0:
                click.echo(' ' * indent, nl=False)
                click.secho('[%s] ' % prefix, bold=True, nl=False)

            click.echo(e.timestamp.strftime('%x %X'), nl=False)
            click.echo(' - ', nl=False)
            click.secho(e.resource_status, nl=False,
                        **STACK_STATUS_TO_COLOR[e.resource_status])
            click.echo(' - %s(%s)' % (e.logical_resource_id, e.resource_type),
                       nl=False)

            if e.resource_status_reason:
                click.echo(' - %s' % e.resource_status_reason)
            elif e.physical_resource_id:
                click.echo(' - %s' % e.physical_resource_id)
            else:
                click.echo('')

        else:
            first_run = False

        time.sleep(check_interval)


def start_tail_stack_events_daemon(session,
                                   stack,
                                   latest_events=5,
                                   event_limit=10000,
                                   time_limit=3600,
                                   check_interval=5,
                                   indent=0,
                                   prefix=None):
    thread = threading.Thread(target=tail_stack_events,
                              args=(session,
                                    stack, latest_events, event_limit,
                                    time_limit, check_interval,
                                    indent, prefix))
    thread.daemon = True
    thread.start()
