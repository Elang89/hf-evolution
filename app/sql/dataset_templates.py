

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
{%- endfor -%}
"""