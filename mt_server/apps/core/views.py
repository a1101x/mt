import json

from django.utils.translation import ugettext as _

from celery import current_app
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK

from apps.api.permissions import IsAdmin
from apps.core.serializers import (WorkerSerializer, CancelConsumerSerializer)
from apps.core.tasks import test_task



class TestViewSet(generics.GenericAPIView):
    """
    get:
        Start test task.
    """
    permission_classes = (IsAdmin,)

    def get(self, request, *args, **kwargs):
        """
        # Start test task.
        """
        for i in range(1):
            test_task.delay(1)

        return Response({
            'status': 'success',
            'detail': _('We are generating your random users!')
        }, status=HTTP_200_OK)


class WorkersViewSet(generics.GenericAPIView):
    """
    get:
        Ping all workers.
    post:
        Shutdown selected workers.
    """
    serializer_class = WorkerSerializer
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        return self.serializer_class

    def get(self, request):
        """
        # Ping all existing workers.
        """
        return Response(current_app.control.inspect().ping())

    def post(self, request):
        """
        # Shutdown selected workers.
        """
        shutdown = request.data.get('shutdown', None)
        serializer = WorkerSerializer(data={'shutdown': shutdown})

        if serializer.is_valid():
            if 'all' in shutdown:
                try:
                    current_app.control.broadcast('shutdown')
                    return Response({
                        'status': 'success', 
                        'detail': _('All workers had been shutted down.')
                    }, status=HTTP_200_OK)
                except:
                    raise ValidationError({
                        'status': 'unsuccess', 
                        'detail': _('Error. Something went wrong while shutting down workers.')
                    })
            else:
                statuses = []
                for worker in shutdown:
                    try:
                        pong = current_app.control.ping([worker])

                        if pong:
                            current_app.control.broadcast('shutdown', destination=[worker])
                            statuses.append(worker)
                    except:
                        raise ValidationError({
                            'status': 'unsuccess', 
                            'detail': _('Error. Something went wrong while shutting down ') + '{}.'.format(worker)
                        })       
                return Response({
                    'status': 'success',
                    'detail': '{}'.format(statuses) + _(' had been shutted down.')
                }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess', 
                'errors': serializer.errors
            })


class CancelConsumer(generics.GenericAPIView):
    """
    post:
        Cancel consumer.
    """
    serializer_class = CancelConsumerSerializer
    permission_classes = (IsAdmin,)

    def get_serializer_class(self):
        return self.serializer_class

    def post(self, request):
        """
        # Cancel selected consumer.
        """
        consumer = request.data.get('consumer', None)
        destination = request.data.get('destination', None)

        serializer = CancelConsumerSerializer(data={'consumer': consumer, 'destination': destination})

        if serializer.is_valid():
            current_app.control.cancel_consumer(queue=consumer, destination=destination, reply=True)
            return Response({
                'status': 'success',
                'detail': '{}'.format(consumer) + _(' had been canceled on worker ') + '{}'.format(destination)
            }, status=HTTP_200_OK)
        else:
            raise ValidationError({
                'status': 'unsuccess',
                'errors': serializer.errors
            })
