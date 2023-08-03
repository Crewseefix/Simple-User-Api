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
        """
            returns a list of all users
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    def post(self, request):
        """
            creates a new user
        """
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserDetailsAndUpdate(APIView):
    def get(self, request, id):
        """
            gets the user with the id specified in the url i.e. 'api/url/id'
        """
        try:
            user = User.objects.get(pk=id)
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)
    def patch(self, request, id):
        
        """
            updates the user with the id specified in the url i.e. 'api/url/id
            request is received as JSON in the format:
                {
                    ...
                    "username": "", 
                    "first_name": ""
                    ...
                } 
        """
        try:
            user = User.objects.get(pk=id)
        except Exception:
            return Response({"error": "Object not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UserSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    def delete(self, request, id):
        """
            deletes the user with the id specified in the url i.e. 'api/url/id
        """
        try:
            user = User.objects.get(pk=id)
            user.delete()
            return Response({"message": "User deleted successfully."}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)


class MultipleUsersUpdate(APIView):
    def post(self, request):
        """
        creates multiple users
        request is received as JSON in the format:
            {
                "data":
                    {
                        "username": "", 
                        "first_name": "",
                        "last_name": "",
                        "email"
                    },
                    {
                        "username": "", 
                        "first_name": "",
                        "last_name": "",
                        "email"
                    }
                    ...
            }
        """
        data = request.data.get('data', [])

        users_to_create = []
        response = {'users_not_created': []}
        for user_data in data:
            serializer = UserSerializer(data=user_data)
            if serializer.is_valid():
                users_to_create.append(serializer.save())
            else:
                response.get('users_not_created').append({"users_data": user_data, "error": serializer.errors})
        response["users_created"]=UserSerializer(users_to_create, many=True).data
        return Response(response, status=status.HTTP_200_OK)
    def patch(self, request):
        """
        updates multiple users
        request is received as JSON in the format:
            {
                "data":
                    {
                        ...
                        "first_name": "",
                        "last_name": "",
                        ...
                    },
                    {
                        ...
                        "first_name": "",
                        "last_name": "",
                        ...
                    }
                    ...
            }
        """
        data = request.data.get('data', [])

        response = {'users_updated': [], 'users_not_updated': []}
        for user_data in data:
            user_id = user_data.get('id', None)
            if user_id is None:
                response.get('users_not_updated').append({"users_id": user_id, "error": "User ID not provided."})
            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                response.get('users_not_updated').append({"users_id": user_id, "error": "User not found."})
                continue

            serializer = UserSerializer(user, data=user_data, partial=True)
            if not serializer.is_valid():
                response.get('users_not_updated').append({"users_id": user_id, "error": "User not found."})

            serializer.save()
            response.get('users_updated').append(serializer.data)
        return Response(response, status=status.HTTP_200_OK)
    def delete(self, request):
        """
        deletes multiple users
        request is received as JSON in the format:
            {
                "data": ["1", "2", "3",...]
            }
        """
        data = request.data.get('data', [])
        response = []
        for user_id in data:
            if user_id is None:
                response.append({"id": user_id, "error": "User ID not provided."})
            try:
                user = User.objects.get(pk=user_id)
                user.delete()
                response.append({"id": user_id, "status": "User deleted."})
            except User.DoesNotExist:
                response.append({"id": user_id, "error": f"User with ID {user_id} not found."})

        return Response(response, status=status.HTTP_200_OK)

class MultipleUsersCreateUpdateAndDelete(APIView):
    """
        creates, updates and deletes multiple users
        request is received as JSON in the format:
            {
                "data":
                    [
                        {
                            "id": ""
                        },
                        {
                            ...
                            "id": "",
                            "first_name": "",
                            ...
                        },
                        {
                            "first_name": "",
                            "last_name": "",
                            "username": "",
                            "email": ""
                        }
                    ]
            }
    """
    def post(self, request):
        data = request.data.get('data', [])
        create_response = {'users_created': [], 'users_not_created': []}
        update_response = {'users_updated': [], 'users_not_updated': []}
        delete_response = []
        for user_data in data:
            if user_id := user_data.get('id', None):
                if len(user_data) == 1:
                    if user_id is None:
                        delete_response.append({"id": user_id, "error": "User ID not provided."})
                    try:
                        user = User.objects.get(pk=user_id)
                        user.delete()
                        delete_response.append({"id": user_id, "status": "User deleted."})
                    except User.DoesNotExist:
                        delete_response.append({"id": user_id, "error": f"User with ID {user_id} not found."})
                else:
                    user_id = user_data.get('id', None)
                    if user_id is None:
                        update_response.get('users_not_updated').append({"users_id": user_id, "error": "User ID not provided."})
                    try:
                        user = User.objects.get(pk=user_id)
                    except User.DoesNotExist:
                        update_response.get('users_not_updated').append({"users_id": user_id, "error": "User not found."})
                        continue

                    serializer = UserSerializer(user, data=user_data, partial=True)
                    if not serializer.is_valid():
                        update_response.get('users_not_updated').append({"users_id": user_id, "error": "User not found."})

                    serializer.save()
                    update_response.get('users_updated').append(serializer.data)
            else:
                users_to_create = []
                serializer = UserSerializer(data=user_data)
                if serializer.is_valid():
                    users_to_create.append(serializer.save())
                else:
                    create_response.get('users_not_created').append({"users_data": user_data, "error": serializer.errors})
                create_response.get("users_created").append(UserSerializer(users_to_create, many=True).data)
        response = [
            create_response, 
            update_response, 
            delete_response
        ]
        

        return Response(response, status=status.HTTP_200_OK)