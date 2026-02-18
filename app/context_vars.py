import contextvars

# Variable de contexto para el member_id del tenant actual
# Se usa para que servicios como TokenManager sepan qué tenant está operando
# sin tener que pasar el ID explícitamente en cada función.
member_id_var: contextvars.ContextVar[str] = contextvars.ContextVar("member_id", default="")
