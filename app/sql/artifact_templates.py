_VERIFY_TEMPLATE = "SELECT EXISTS (SELECT 1 FROM {{ table }} WHERE id = {{ id }})"

_INSERT_TEMPLATE = """INSERT INTO {{ table }} (
    {%- for param in params -%}
        {{ param }}
        {%- if not loop.last -%}
            ,
        {%- endif -%}
    {%- endfor -%}
) VALUES  
{%- for value in values -%}
   {{ value }}

    {%- if not loop.last -%}
        ,
    {%- endif -%}
{%- endfor -%}
RETURNING id 
"""