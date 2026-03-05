# 共用账号与权限管理API文档

## 1. 系统概述

本文档描述了与HOJ项目共用账号与权限管理系统的API接口规范，旨在帮助另一个项目实现与HOJ项目的用户账号共享和权限管理。

### 1.1 核心功能

- 用户注册与登录
- JWT令牌认证
- 角色与权限管理
- 用户信息获取与更新

### 1.2 技术栈

- Spring Boot
- Apache Shiro
- JWT (JSON Web Token)
- Redis (用于令牌存储与管理)
- MySQL (共享数据库)

## 2. 数据库结构

### 2.1 核心表结构

#### 2.1.1 用户表 (user_info)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| uuid | VARCHAR(36) | 用户唯一标识 |
| username | VARCHAR(20) | 用户名 |
| password | VARCHAR(32) | MD5加密后的密码 |
| email | VARCHAR(100) | 邮箱 |
| nickname | VARCHAR(50) | 昵称 |
| avatar | VARCHAR(255) | 头像URL |
| status | TINYINT | 状态（0:正常, 1:封禁） |
| gmt_create | DATETIME | 创建时间 |
| gmt_modified | DATETIME | 修改时间 |
| ... | ... | 其他用户信息字段 |

#### 2.1.2 角色表 (role)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | BIGINT | 角色ID |
| role | VARCHAR(20) | 角色名称 (如: user, admin, root) |
| description | VARCHAR(255) | 角色描述 |
| status | TINYINT | 状态（0:可用, 1:不可用） |
| gmt_create | DATETIME | 创建时间 |
| gmt_modified | DATETIME | 修改时间 |

#### 2.1.3 权限表 (auth)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | BIGINT | 权限ID |
| permission | VARCHAR(50) | 权限标识 (如: user:list, problem:add) |
| name | VARCHAR(50) | 权限名称 |
| status | TINYINT | 状态（0:可用, 1:不可用） |
| gmt_create | DATETIME | 创建时间 |
| gmt_modified | DATETIME | 修改时间 |

#### 2.1.4 用户角色关联表 (user_role)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | BIGINT | 关联ID |
| uid | VARCHAR(36) | 用户ID |
| rid | BIGINT | 角色ID |
| gmt_create | DATETIME | 创建时间 |

#### 2.1.5 角色权限关联表 (role_auth)

| 字段名 | 数据类型 | 描述 |
|-------|---------|------|
| id | BIGINT | 关联ID |
| rid | BIGINT | 角色ID |
| aid | BIGINT | 权限ID |
| gmt_create | DATETIME | 创建时间 |

## 3. API接口规范

### 3.1 基础信息

- API版本: v1
- 基础URL: `http://localhost:6688/api`
- 认证方式: JWT Token (在请求头中添加 `Authorization: Bearer {token}`)
- 响应格式: JSON

### 3.1.1 服务端口配置

| 服务名称 | 默认端口 | 说明 |
|---------|---------|------|
| 后端服务 | 6688 | HOJ项目的主要API服务 |
| MySQL数据库 | 3306 | 共享数据库服务 |
| Redis | 6379 | 用于存储Token和会话信息 |
| Nacos | 8848 | 配置中心服务 |

### 3.2 统一响应格式

```json
{
  "status": 200,
  "message": "success",
  "data": {}
}
```

### 3.3 错误码

| 错误码 | 描述 |
|-------|------|
| 400 | 请求参数错误 |
| 401 | 未认证或认证失败 |
| 403 | 无权限访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

## 4. 认证相关接口

### 4.1 用户注册

**接口地址**: `POST /register`

**请求参数**:

```json
{
  "username": "testuser",
  "password": "123456",
  "email": "test@example.com",
  "code": "123456",
  "nickname": "测试用户"
}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": null
}
```

### 4.2 获取注册验证码

**接口地址**: `GET /get-register-code`

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| email | String | 是 | 用户邮箱 |

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "email": "test@example.com",
    "expire": 600
  }
}
```

### 4.3 用户登录

**接口地址**: `POST /login`

**请求参数**:

```json
{
  "username": "testuser",
  "password": "123456"
}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "uid": "uuid-123456",
    "username": "testuser",
    "nickname": "测试用户",
    "avatar": "https://example.com/avatar.jpg",
    "roleList": ["user"]
  }
}
```

**说明**: 登录成功后，服务器会在响应头中返回JWT令牌：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 4.4 退出登录

**接口地址**: `GET /logout`

**请求头**:

```
Authorization: Bearer {token}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": null
}
```

### 4.5 刷新令牌

**接口地址**: `POST /refresh-token`

**请求头**:

```
Authorization: Bearer {token}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }
}
```

## 5. 用户信息相关接口

### 5.1 获取当前用户信息

**接口地址**: `GET /user/info`

**请求头**:

```
Authorization: Bearer {token}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "uid": "uuid-123456",
    "username": "testuser",
    "nickname": "测试用户",
    "email": "test@example.com",
    "avatar": "https://example.com/avatar.jpg",
    "roleList": ["user"]
  }
}
```

### 5.2 更新用户信息

**接口地址**: `PUT /user/info`

**请求头**:

```
Authorization: Bearer {token}
```

**请求参数**:

```json
{
  "nickname": "新昵称",
  "avatar": "https://example.com/new-avatar.jpg",
  "signature": "个性签名"
}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": null
}
```

### 5.3 修改密码

**接口地址**: `POST /user/change-password`

**请求头**:

```
Authorization: Bearer {token}
```

**请求参数**:

```json
{
  "oldPassword": "123456",
  "newPassword": "654321"
}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": null
}
```

## 6. 权限相关接口

### 6.1 获取用户权限信息

**接口地址**: `GET /user/auth-info`

**请求头**:

```
Authorization: Bearer {token}
```

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "roles": ["user", "admin"],
    "permissions": ["user:list", "user:edit", "problem:add"]
  }
}
```

### 6.2 检查权限

**接口地址**: `GET /check-permission`

**请求头**:

```
Authorization: Bearer {token}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| permission | String | 是 | 权限标识 |

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "hasPermission": true
  }
}
```

### 6.3 检查角色

**接口地址**: `GET /check-role`

**请求头**:

```
Authorization: Bearer {token}
```

**请求参数**:

| 参数名 | 类型 | 必填 | 描述 |
|-------|------|------|------|
| role | String | 是 | 角色名称 |

**响应示例**:

```json
{
  "status": 200,
  "message": "success",
  "data": {
    "hasRole": true
  }
}
```

## 7. JWT Token使用规范

### 7.1 Token获取

用户登录成功后，服务器会在响应头中返回JWT令牌：

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

### 7.2 Token使用

在需要认证的API请求中，需在请求头中添加Token：

```
Authorization: Bearer {token}
```

### 7.3 Token过期与刷新

- Token默认有效期为2小时
- 可通过`/refresh-token`接口刷新Token
- 刷新Token的有效期为7天

### 7.4 Token验证失败处理

当Token验证失败时，服务器会返回401错误，客户端需处理以下情况：

1. Token过期 - 调用刷新接口获取新Token
2. Token无效 - 引导用户重新登录
3. Token被吊销 - 引导用户重新登录

## 8. 权限管理实现建议

### 8.1 权限验证方式

1. **基于注解的权限验证**:

```java
@RequiresAuthentication  // 需要认证
@RequiresRoles("admin")   // 需要admin角色
@RequiresPermissions("user:edit")  // 需要user:edit权限
public CommonResult<UserInfoVO> updateUser(UserInfoVO userInfoVo) {
    // 业务逻辑
}
```

2. **编程式权限验证**:

```java
if (SecurityUtils.getSubject().hasPermission("user:edit")) {
    // 执行有权限的操作
} else {
    // 无权限处理
}
```

### 8.2 权限设计原则

1. **最小权限原则** - 仅授予用户完成任务所需的最小权限
2. **角色分离原则** - 不同角色负责不同职责
3. **权限继承原则** - 高级角色继承低级角色的权限

## 9. 安全注意事项

### 9.1 密码安全

- 密码必须经过MD5加密后存储
- 密码长度不少于6位
- 定期提示用户修改密码

### 9.2 Token安全

- 避免将Token存储在 localStorage 中，建议使用 HttpOnly Cookie
- 定期更换Token密钥
- 实现Token黑名单机制

### 9.3 接口安全

- 所有接口都应进行参数验证
- 对敏感操作添加频率限制
- 实现防CSRF攻击机制

## 10. 整合示例

### 10.1 Spring Boot整合JWT示例

```java
@Configuration
public class WebSecurityConfig extends WebMvcConfigurerAdapter {
    
    @Bean
    public JwtAuthenticationFilter jwtAuthenticationFilter() {
        return new JwtAuthenticationFilter();
    }
    
    @Override
    public void addInterceptors(InterceptorRegistry registry) {
        registry.addInterceptor(jwtAuthenticationFilter())
                .addPathPatterns("/api/**")
                .excludePathPatterns("/api/login", "/api/register", "/api/get-register-code");
    }
}
```

### 10.2 JWT验证过滤器示例

```java
@Component
public class JwtAuthenticationFilter extends OncePerRequestFilter {
    
    @Autowired
    private JwtUtils jwtUtils;
    
    @Override
    protected void doFilterInternal(HttpServletRequest request, HttpServletResponse response, FilterChain filterChain) throws ServletException, IOException {
        String token = request.getHeader("Authorization");
        
        if (token != null && token.startsWith("Bearer ")) {
            token = token.substring(7);
            
            try {
                Claims claims = jwtUtils.getClaimByToken(token);
                if (claims != null && !jwtUtils.isTokenExpired(claims.getExpiration())) {
                    String userId = claims.getSubject();
                    // 验证Token是否在Redis中存在
                    if (jwtUtils.hasToken(userId)) {
                        // 设置用户信息到上下文
                        // ...
                    }
                }
            } catch (Exception e) {
                // Token验证失败
            }
        }
        
        filterChain.doFilter(request, response);
    }
}
```

## 11. 常见问题

### 11.1 如何处理用户在两个系统中的权限差异？

建议在权限设计时，为不同系统定义不同的权限前缀，例如：

- HOJ系统：`hoj:problem:add`, `hoj:contest:create`
- 新系统：`newsys:article:add`, `newsys:comment:edit`

这样可以实现两个系统的权限隔离与共享。

### 11.2 如何处理用户登录状态同步？

由于使用了共享的Redis存储Token，用户在一个系统登录或退出时，另一个系统的Token状态会自动同步。

### 11.3 如何扩展新的角色和权限？

可以直接在共享数据库中添加新的角色和权限记录，并通过角色权限关联表为用户分配新的角色和权限。

## 12. 联系方式

如有任何问题或建议，请联系系统管理员。

---

**文档版本**: 1.0
**最后更新**: 2026-03-04
**作者**: AI Assistant