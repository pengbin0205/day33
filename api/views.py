from rest_framework.response import Response
from rest_framework.views import APIView

from api.models import Book
from api.serializer import BookModelSerializer, BookDeModelSerializer, BookModelSerializerV2


class BookAPIView(APIView):

    def get(self, request, *args, **kwargs):
        """
        查询单个图书  查询所有图书
        """
        book_id = kwargs.get("id")

        if book_id:
            book_obj = Book.objects.get(pk=book_id)
            book_serializer = BookModelSerializer(book_obj).data

            return Response({
                "status": 200,
                "message": "查询成功",
                "results": book_serializer
            })
        else:

            book_set = Book.objects.all()
            book_set_serializer = BookModelSerializer(book_set, many=True).data

            return Response({
                "status": 200,
                "message": "查询成功",
                "results": book_set_serializer
            })

    def post(self, request, *args, **kwargs):
        """
        完成对象的新增
        """
        request_data = request.data

        # 将前端传递的参数交给反序列化器进行校验
        serializer = BookDeModelSerializer(data=request_data)

        # 校验数据是否合法 raise_exception: 一旦校验失败，立即抛出异常
        serializer.is_valid(raise_exception=True)
        book_obj = serializer.save()

        return Response({
            "status": 201,
            "message": "创建成功",
            "results": BookModelSerializer(book_obj).data
        })

    def delete(self, request, *args, **kwargs):
        """
                删除单个对象以及删除多个对象
                单个删除：通过url传递id 即可  v2/books/1/
                删除多个：有多个id
                """

        book_id = kwargs.get("id")

        if book_id:
            # 如果路径中存在id  代表删除单个
            # 将删除单个转换为删除多个执行
            ids = [book_id]
        else:
            # 代表要删除多个
            ids = request.data.get("ids")
        print(ids)
        # 判断要删除的图书是否存在 且还未删除
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        if response:
            return Response({
                "status": 200,
                "message": "删除成功"
            })

        return Response({
            "status": 400,
            "message": "删除失败或删除的图书不存在"
        })

    def put(self, request, *args, **kwargs):
        """
                修改单个对象的全部字段
                全部字段：指的是所有参与反序列化的字段
                参数：要修改的值  要修改的图书的id
                :return: 修改后的对象
                """
        # 要修改的值
        request_data = request.data
        # 图书id
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({
                "status": 400,
                "message": "图书不存在"
            })
        # 前端传递过来的要修改的值  更新数据时需要校验
        book_serializer = BookModelSerializer(data=request_data, instance=book_obj)
        book_serializer.is_valid(raise_exception=True)

        # 经过序列序列化器校验后，保存修改的值
        # 如果调用序列化器时指定了关键字参数 instance, 则底层会调用update()完成更新
        book = book_serializer.save()

        return Response({
            "status": 200,
            "message": "修改成功",
            "results": BookModelSerializer(book).data
        })

    def patch(self, request, *args, **kwargs):
        """
                完成修改单个对象的某些字段
                """

        request_data = request.data
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({
                "status": 400,
                "message": "图书不存在"
            })

        # 如果要修改部分字段，只需要指定参数partial=True即可
        book_serializer = BookModelSerializer(data=request_data, instance=book_obj, partial=True)
        book_serializer.is_valid(raise_exception=True)

        book = book_serializer.save()

        return Response({
            "status": 200,
            "message": "修改成功",
            "results": BookModelSerializer(book).data
        })


"""
查询单个  查询所有  新增单个  新增多个     
删除单个 删除多个  修改单个  局部修改单个  修改多个 局部修改多个
"""


class BookAPIViewV2(APIView):
    def get(self, request, *args, **kwargs):
        """
        查询单个图书  查询所有图书
        """
        book_id = kwargs.get("id")

        if book_id:
            book_obj = Book.objects.get(pk=book_id)
            book_serializer = BookModelSerializerV2(book_obj).data

            return Response({
                "status": 200,
                "message": "查询成功",
                "results": book_serializer
            })
        else:

            book_set = Book.objects.all()
            book_set_serializer = BookModelSerializerV2(book_set, many=True).data

            return Response({
                "status": 200,
                "message": "查询成功",
                "results": book_set_serializer
            })

    def post(self, request, *args, **kwargs):
        """
        增加单个：{} 前端传递参数的格式  字典
        增加多个：[{},{},{}] 列表中嵌套字典 一个字典是一个新增的
        """
        request_data = request.data

        if isinstance(request_data, dict):  # 代表新增单个图书
            many = False

        elif isinstance(request_data, list):  # 代表新增多个图书
            # 如果一次新增多个对象 需要指定参数 many=True
            many = True
        else:
            return Response({
                "status": 400,
                "message": "请求参数格式有误"
            })

        # 将前端传递的参数交给反序列化器进行校验
        serializer = BookModelSerializerV2(data=request_data, many=many)

        # 校验数据是否合法 raise_exception: 一旦校验失败，立即抛出异常
        serializer.is_valid(raise_exception=True)
        book_obj = serializer.save()

        return Response({
            "status": 201,
            "message": "创建成功",
            "results": BookModelSerializerV2(book_obj, many=many).data
        })

    def delete(self, request, *args, **kwargs):
        """
        删除单个对象以及删除多个对象
        单个删除：通过url传递id 即可  v2/books/1/
        删除多个：有多个id
        """

        book_id = kwargs.get("id")

        if book_id:
            # 如果路径中存在id  代表删除单个
            # 将删除单个转换为删除多个执行
            ids = [book_id]
        else:
            # 代表要删除多个
            ids = request.data.get("ids")
        print(ids)
        # 判断要删除的图书是否存在 且还未删除
        response = Book.objects.filter(pk__in=ids, is_delete=False).update(is_delete=True)
        if response:
            return Response({
                "status": 200,
                "message": "删除成功"
            })

        return Response({
            "status": 400,
            "message": "删除失败或删除的图书不存在"
        })

    def put(self, request, *args, **kwargs):
        """
        修改单个对象的全部字段
        全部字段：指的是所有参与反序列化的字段
        参数：要修改的值  要修改的图书的id
        :return: 修改后的对象
        """
        # 要修改的值
        request_data = request.data
        # 图书id
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({
                "status": 400,
                "message": "图书不存在"
            })
        # request_data: 前端传递过来的要修改的值  更新数据时需要校验
        # TODO 需要指定关键字参数 instance 将要修改的对象传递给序列化器
        book_serializer = BookModelSerializerV2(data=request_data, instance=book_obj)
        book_serializer.is_valid(raise_exception=True)

        # 经过序列序列化器校验后，保存修改的值
        # 如果调用序列化器时指定了关键字参数 instance, 则底层会调用update()完成更新
        book = book_serializer.save()

        return Response({
            "status": 200,
            "message": "修改成功",
            "results": BookModelSerializerV2(book).data
        })

    def patch(self, request, *args, **kwargs):
        """
        完成修改单个对象的某些字段
        """

        request_data = request.data
        book_id = kwargs.get("id")

        try:
            book_obj = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({
                "status": 400,
                "message": "图书不存在"
            })

        # 如果要修改部分字段，只需要指定参数partial=True即可
        book_serializer = BookModelSerializerV2(data=request_data, instance=book_obj, partial=True)
        book_serializer.is_valid(raise_exception=True)

        book = book_serializer.save()

        return Response({
            "status": 200,
            "message": "修改成功",
            "results": BookModelSerializerV2(book).data
        })
