_GET_TEMPLATE = "SELECT id FROM {{ table }} WHERE repository_name = '{{ value }}'"

_INSERT_TEMPLATE = """INSERT INTO {{ table }} (
    {%- for param in params -%}
        {{ param }}
        {%- if not loop.last -%}
            ,
        {%- endif -%}
    {%- endfor -%}
) VALUES (
    {%- for _ in range(tup_size) -%}
        %s
        {%- if not loop.last -%}
            ,
        {%- endif -%}
    {%- endfor -%}
)
"""