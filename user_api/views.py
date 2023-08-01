from django.http import JsonResponse, QueryDict
from django.views.decorators.csrf import csrf_exempt
from .models import User
from .serializers import UserSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
import pdb


class UserListAndCreate(APIView):
    def get(self, request):
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsAndUpdate(APIView):
    def get(self, request, id):
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, id):
        try:
            user = User.objects.get(pk=id)
        except user.DoesNotExist:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id):
        try:
            user = User.objects.get(pk=id)
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class MultipleUsersUpdate(APIView):
    def post(self, request):
        data = request.data.get('data', [])

        users_to_create = []
        for user_data in data:
            serializer = UserSerializer(data=user_data)
            pdb.set_trace()
            if serializer.is_valid():
                users_to_create.append(serializer.save())
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response(UserSerializer(users_to_create, many=True).data, status=status.HTTP_201_CREATED)
    def patch(self, request):
        data = request.data.get('data', [])

        updated_users = []
        for user_data in data:
            user_id = user_data.get('id', None)
            if user_id is None:
                return Response({"error": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)

            serializer = UserSerializer(user, data=user_data, partial=True)
            if not serializer.is_valid():
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

            serializer.save()
            updated_users.append(serializer.data)
        return Response(updated_users, status=status.HTTP_200_OK)
    def delete(self, request):
        data = request.data.get('data', [])

        deleted_user_ids = []
        for user_data in data:
            user_id = user_data.get('id', None)
            if user_id is None:
                return Response({"error": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                deleted_user_ids.append(user_id)
            except User.DoesNotExist:
                return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)

        return Response({"deleted_user_ids": deleted_user_ids}, status=status.HTTP_200_OK)

class MultipleUsersCreateUpdateAndDelete(APIView):
    def post(self, request):
        data = request.data.get('data', [])

        created_users = []
        updated_users = []
        deleted_user_ids = []

        for user_data in data:
            if user_id := user_data.get('id', None):
                if len(user_data) == 1:
                    # It's a delete request
                    try:
                        user = User.objects.get(pk=user_id)
                        user.delete()
                        deleted_user_ids.append(user_id)
                    except User.DoesNotExist:
                        return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)
                else:
                    # It's an update request
                    try:
                        user = User.objects.get(pk=user_id)
                        serializer = UserSerializer(user, data=user_data, partial=True)
                        if not serializer.is_valid():
                            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        serializer.save()
                        updated_users.append(serializer.data)
                    except User.DoesNotExist:
                        return Response({"error": f"User with ID {user_id} not found."}, status=status.HTTP_404_NOT_FOUND)
            else:
                # It's a create request
                serializer = UserSerializer(data=user_data)
                if not serializer.is_valid():
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

                serializer.save()
                created_users.append(serializer.data)
        response_data = {
            "created_users": created_users,
            "updated_users": updated_users,
            "deleted_user_ids": deleted_user_ids,
        }

        return Response(response_data, status=status.HTTP_200_OK)