_AUTHOR_TEMPLATE = "SELECT id FROM authors WHERE name = '{{ value }}'"

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