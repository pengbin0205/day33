from rest_framework.serializers import ModelSerializer
from rest_framework import serializers, exceptions

from api.models import Book, Press


class PressModeSerializer(ModelSerializer):
    """出版社序列化器"""

    class Meta:
        model = Press
        fields = ("press_name", "address", "pic")


class BookModelSerializer(ModelSerializer):
    """图书的序列化器"""

    # TODO 多表连表查询  查询图书时将图书对应的出版社信息查询出来
    # 可以在一个序列化器中嵌套另外一个序列化器来完成多表查询
    # 关联序列化器的名称必须是外键，否则报错
    publish = PressModeSerializer()

    class Meta:
        # 指定当前序列化器要序列化器的模型
        model = Book
        # 指定你要序列化该模型的那些字段
        # fields = ("book_name", "price", "pic", "publish_name", "press_address", "author_list")
        fields = ("book_name", "price", "pic", "publish", "author_list")



class BookDeModelSerializer(ModelSerializer):
    """
    反序列化器  数据入库时使用
    """

    class Meta:
        model = Book
        # 指定反序列化需要的字段
        fields = ("book_name", "price", "publish", "authors")

        # 添加DRF官方所提供的校验规则
        extra_kwargs = {
            "book_name": {
                "required": True,  # 设置为必填项
                "min_length": 3,  # 最小长度
                "error_messages": {
                    "required": "图书名是必填的",
                    "min_length": "图书名长度太短了"
                }
            },
            "price": {
                "max_digits": 5,
            }
        }

    def validate_book_name(self, value):
        book = Book.objects.filter(book_name=value)
        if book:
            raise exceptions.ValidationError("图书名已存在")
        return value

    def validate(self, attrs):
        # 可以自定义校验规则
        return attrs

    # TODO 无需重写create()方法，因为在ModelSerializer已经完成了该方法的重写





class BookModelSerializerV2(ModelSerializer):
    """序列化器与反序列化器整合"""

    class Meta:
        model = Book
        # 字段应该写哪些  应该写参与序列化与反序列化的并集
        fields = ("book_name", "price", "publish", "authors", "pic")

        # 添加DRF官方所提供的校验规则
        # TODO 可以在此参数中指定哪些字段是只参与序列化 哪些字段只参与反序列化
        extra_kwargs = {
            "book_name": {
                "required": True,  # 设置为必填项
                "min_length": 3,  # 最小长度
                "error_messages": {
                    "required": "图书名是必填的",
                    "min_length": "图书名长度太短了"
                }
            },
            # 指定该字段只参与反序列化  保存时提交
            "publish": {
                "write_only": True,
            },
            "authors": {
                "write_only": True,
            },
            # 指定该字段只参与序列化  查询时使用
            "pic": {
                "read_only": True
            }
        }

    def validate_book_name(self, value):
        book = Book.objects.filter(book_name=value)
        if book:
            raise exceptions.ValidationError("图书名已存在")
        return value

    def validate(self, attrs):
        # 可以自定义校验规则
        price = attrs.get("price")
        if price > 1000:
            raise exceptions.ValidationError("超过最高价格了~~")
        return attrs

    # 重写update方法完成保存
    # def update(self, instance, validated_data):
    #     # instance：当前要修改的实例
    #     # validated_data：要修改的值
    #     book_name = validated_data.get("book_name")
    #     instance.book_name = book_name
    #     instance.save()
    #
    #     return instance
