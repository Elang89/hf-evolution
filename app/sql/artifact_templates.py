_VERIFY_TEMPLATE = "SELECT EXISTS (SELECT 1 FROM {{ table }} WHERE id = {{ id }})"

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