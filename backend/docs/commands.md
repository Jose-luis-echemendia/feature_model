# alembic revision --autogenerate -m "Add role column to user table"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.autogenerate.compare] Detected removed table 'item'
INFO  [alembic.autogenerate.compare] Detected removed index 'ix_user_email' on 'user'
INFO  [alembic.autogenerate.compare] Detected removed table 'user'
  Generating /app/app/alembic/versions/9f7e26899e7c_add_role_column_to_user_table.py ...  done
# alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade 1a31ce608336 -> 9f7e26899e7c, Add role column to user table
# 

