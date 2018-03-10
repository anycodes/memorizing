from django.db import models

# Create your models here.


class User(models.Model):
    userid = models.AutoField(primary_key=True,verbose_name="编号")
    username = models.CharField(max_length=30,verbose_name="姓名")
    password = models.CharField(max_length=30,verbose_name="密码")
    sex = models.CharField(max_length=30,verbose_name="性别")
    school = models.CharField(max_length=30,verbose_name="学校")
    grade = models.CharField(max_length=30,verbose_name="年级")
    qq = models.CharField(max_length=30,verbose_name="QQ号")
    wechat = models.CharField(max_length=30,verbose_name="微信标识")
    email = models.CharField(max_length=50,verbose_name="邮箱")

    class Meta:
        verbose_name = "用户"
        verbose_name_plural = verbose_name
        ordering = ["-userid"]

    def __str__(self):
        return self.username


class Catagory(models.Model):
    catid = models.AutoField(primary_key=True, verbose_name="编号")
    name = models.CharField(max_length=120, verbose_name="名称")
    first = models.CharField(max_length=30,verbose_name="一级分类")
    second = models.CharField(max_length=30,null=False,blank=True, verbose_name="二级分类")
    third = models.CharField(max_length=30,null=False,blank=True, verbose_name="三级分类")
    forth = models.CharField(max_length=30,null=False,blank=True, verbose_name="四级分类")

    class Meta:
        verbose_name = "分类"
        verbose_name_plural = verbose_name
        ordering = ["-catid"]

    def __str__(self):
        return self.name


class Word(models.Model):
    wordid = models.AutoField(primary_key=True, verbose_name="编号")
    word = models.CharField(max_length=100,verbose_name="单词")
    mean_en = models.TextField(max_length=1000,verbose_name="英文解释")
    mean_zh = models.CharField(max_length=1000, verbose_name="中文释义")
    catagory = models.ManyToManyField(Catagory,verbose_name="标签")

    class Meta:
        verbose_name = "单词"
        verbose_name_plural = verbose_name
        ordering = ["-wordid"]

    def __str__(self):
        return self.word


class History(models.Model):
    hisid = models.AutoField(primary_key=True, verbose_name="编号")
    user = models.ForeignKey(User,verbose_name="用户")
    catagory = models.ForeignKey(Catagory,verbose_name="分类")
    grade = models.CharField(max_length=200, verbose_name="分数")
    date = models.DateTimeField(auto_now=True,verbose_name="时间")

    class Meta:
        verbose_name = "历史"
        verbose_name_plural = verbose_name
        ordering = ["-hisid"]


class Wrong(models.Model):
    wrongid = models.AutoField(primary_key=True, verbose_name="编号")
    user = models.ForeignKey(User,verbose_name="用户")
    word = models.ForeignKey(Word,verbose_name="单词")
    times = models.IntegerField(default=1,verbose_name="次数")
    date = models.DateTimeField(auto_now=True, verbose_name="时间")

    class Meta:
        verbose_name = "错误记录"
        verbose_name_plural = verbose_name
        ordering = ["-wrongid"]
