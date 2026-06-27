# 学习笔记：Python 中的 `@property` 和 `@setter`

在面向对象编程中，我们经常需要对类中的属性进行封装，比如在给属性赋值时进行数据验证、转换或者加密。Python 提供了 `@property` 装饰器来实现这种优雅的属性封装。

## 基本概念

* `@property`：将一个方法变成属性的**读取器 (Getter)**。让你可以像访问属性一样（不需要加括号）访问这个方法的返回值。
* `@<属性名>.setter`：将一个方法变成属性的**设置器 (Setter)**。当你在代码中给这个属性赋值（用 `=` 号）时，实际上会自动调用这个方法。

## 在本项目的应用案例 (密码加密处理)

在 `models/user.py` 中，我们有一个 `User` 类，其中定义了和密码相关的方法：

```python
from pwdlib import PasswordHash
password_hash = PasswordHash.recommended()

class User:
    def __init__(self):
        # 实际存储在数据库中的是加密后的密码。
        # 我们用单下划线开头的 _password 作为一个"私有"属性来存放真正的数据
        self._password = None
  
    # 【读取器】当你获取 user.password 时，实际上返回的是 _password 的值
    @property
    def password(self):
        return self._password
  
    # 【设置器】当你执行 user.password = "123456" 时，会自动触发并运行这个方法
    @password.setter
    def password(self, raw_password: str):
        # 我们在这里拦截了赋值操作，把原始明文密码加密后，存入内部的 _password 属性
        self._password = password_hash.hash(raw_password)
```

### 为什么这样做？

这样设计的好处是，对外部调用者来说，给用户设置密码的操作非常简单和直观，不需要手动去调用加密函数，也不怕忘记加密：

**传统的做法 (没有 property)：**

```python
user = User()
# 外部代码每次创建用户都需要手动加密，很容易因为疏忽导致明文密码直接存入数据库
user._password = password_hash.hash("my_secret_password")
```

**优雅的做法 (使用了 property & setter)：**

```python
user = User()
# 就像给普通变量赋值一样简单，底层代码会自动帮你把 "my_secret_password" 进行哈希加密后再存起来！
user.password = "my_secret_password"

# 初始化时也可以直接传入明文： user = User(password="123456")
```

通过这种方式，我们既保证了外部调用代码的**简洁性**（直接赋值），又保证了内部数据的**安全性与逻辑的一致性**（存入的必定是加密后的密码），这是面向对象编程中“封装”思想的绝佳体现。

---

# 学习笔记：SQLAlchemy 2.0 中的模型字段定义

在 `models/user.py` 中，我们定义数据库表的主键字段时，使用了如下语法：
```python
id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
```
这是 SQLAlchemy 2.0 推荐的最新写法（结合了 Python 的类型注解 Type Hinting）。我们可以把它拆解成左右两部分来看：

## 1. 左半部分：`id: Mapped[int]` (给写代码的人看)
*   `id`：这是我们在 Python 代码里使用的属性名。
*   `Mapped[int]`：这是 Python 的类型注解。它告诉你的代码编辑器（比如 VSCode、PyCharm）：**“这个叫 `id` 的属性，是一个被 SQLAlchemy 映射过的字段，它里面装的绝对是一个整数 (`int`)。”**
*   **好处**：这部分完全是为了提升开发体验的！当你敲下 `user.id` 时，编辑器知道它是个数字，就会自动提示数字相关的操作。如果不写 `Mapped[int]`，编辑器往往不知道这是个啥，也就没法智能提示代码了。

## 2. 右半部分：`= mapped_column(...)` (给数据库看)
这是真正用来配置数据库底层表结构的地方。
*   `mapped_column(...)`：这是 SQLAlchemy 2.0 定义列的核心函数。
*   `Integer`：告诉底层的 MySQL 数据库，这个列对应的数据类型是 `INT`。
*   `primary_key=True`：设置这个列为这张表的**主键 (Primary Key)**。主键就是表中数据的唯一标识（就像身份证号），一条数据必须有一个主键，且绝对不能和别人重复。
*   `autoincrement=True`：开启**自增**。意味着当你往数据库里插入新数据时，你**完全不需要**自己去填这个 `id`，MySQL 数据库会自动在后台按顺序分配 1, 2, 3, 4...

## 总结示例：与其他字段的对比

为了让你更清楚，我们可以对比一下其他字段的写法：

```python
class ExampleUser(Base):
    __tablename__ = "example_user"
    
    # 1. 主键字段：必须是唯一的，且设置了让数据库自动递增
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # 2. 普通整数字段：比如年龄，不需要主键，也不用自增
    age: Mapped[int] = mapped_column(Integer)

    # 3. 字符串字段：比如邮箱，限制最大长度100，并且 unique=True 规定全表不能有重复的邮箱
    email: Mapped[str] = mapped_column(String(100), unique=True)
```

**一句话总结：**
`左边的 Mapped[类型]` 让你敲代码时有**智能提示**，`右边的 mapped_column(规则)` 告诉数据库这个字段**怎么存、有啥限制**。两者结合，完美无缺！

---

# 开发中的常见疑惑解答 (Q&A)

### Q1: `@property` 为什么只给 `password` 用，而像 `email` 这样的字段不用？
**A:** 决定要不要用 `@property` 的标准，是**“在获取或赋值时，是否需要在暗中执行额外的逻辑”**。
*   `email`、`username` 属于“你给什么就是什么”，直接原封不动存入数据库即可，所以直接公开为普通属性。
*   `password` 绝对不能存明文。当外部代码写 `user.password = "123"` 时，我们**必须拦截这个动作**，将其加密成乱码后再存入真正的底层私有变量 `_password` 里。因此需要用 `@property` 和 `@setter` 来伪装和拦截。

### Q2: Python 为什么不一开始就全写成 Getter/Setter，像 Java 那样防患于未然？
**A:** 这正是 Python 优雅的地方。Python 原生支持直接赋值（`user.email = "xxx"`）。如果没有特殊逻辑，写 `@property` 纯属多此一举。
如果将来某天 `email` 真的需要加逻辑（比如验证格式），开发者只需在类内部补上 `@property` 即可，**外部早已写好的调用代码完全不需要做任何修改**。Python 允许你前期图省事，后期也能无缝扩展。

### Q3: 为什么 `models/__init__.py` 里的 `from . import user` 必须写在文件的最后面？
**A:** 为了防止**循环导入（Circular Import）**。
在 `user.py` 中，我们需要 `from . import Base`。如果 `__init__.py` 把导入 `user.py` 的代码放在最前面，Python 就会在还没定义好 `Base` 的时候，直接暂停并跑去执行 `user.py`，导致 `user.py` 找不到 `Base` 从而崩溃报错。把它放在最后，可以确保 `Base` 已经被成功加载到内存中。

### Q4: Alembic 数据库迁移的三个核心命令分别是干嘛的？
**A:** 可以把 Alembic 当作“数据库的 Git”。
1.  `alembic init alembic --template async`：**【建厂】**。只运行一次，初始化 Alembic 环境，生成配置文件夹。
2.  `alembic revision --autogenerate -m "描述"`：**【画图纸】**。对比你的 Python 代码模型和现有的 MySQL 数据库，找出差异，自动生成一份“升级/建表脚本”（但此时还没真正修改数据库）。
3.  `alembic upgrade head`：**【正式施工】**。拿着刚才生成的图纸，去 MySQL 数据库里真正执行 `CREATE TABLE` 等语句，完成表结构的最终同步。

---

# 学习笔记：FastAPI 邮件发送与 Pydantic 踩坑指南

## 1. 邮件配置与发送验证码
我们在路由中实现了通过 `fastapi-mail` 发送验证码：
* 随机生成验证码：`code = "".join(random.choices(string.digits, k=4))`，快速生成4位纯数字。
* 消息构建：通过 `MessageSchema` 构建邮件体，包含接收人 `recipients`、主题 `subject` 及正文 `body`。

## 2. Pydantic 实例化错误 (Class vs Instance)
**踩坑记录**：路由中错误地写了 `return ResponseOut`。
`ResponseOut` 只是一个**类（Class）**，而 FastAPI 进行数据响应序列化时，要求必须返回它的**实例对象（Instance）**或字典。正确的做法是加括号进行实例化：`return ResponseOut(...)`。

## 3. Pydantic Field：Alias (别名) 与 Default (默认值)
在处理缺少参数报错时，我们见证了两种不同的 Pydantic 字段配置方式的区别：

**方式一：使用 alias (别名)**
```python
result: Annotated[Literal["success", "failsure"], Field(alias="success")]
```
这里 `result` 是字段名，但对外暴露的名称是 `success`。
**代价**：在默认配置下，Pydantic 强制要求**在实例化时必须使用别名**。此时你只能写 `ResponseOut(success="success")`，直接写 `ResponseOut()` 会抛出缺少字段的 500 错误。

**方式二：巧妙利用默认值 (Default)**
```python
result: Annotated[Literal["success", "failsure"], Field("success")]
```
将 `"success"` 作为 `Field` 函数的第一个位置参数传入，在源码中这对应的是 `default` 参数。
**优雅之处**：既然这个字段被赋予了默认值 `"success"`，那么实例化时就**不再是必填项**了！现在只需写 `ResponseOut()`，它就能自己完成实例化，完美解决了报错，并且代码更清爽了。
