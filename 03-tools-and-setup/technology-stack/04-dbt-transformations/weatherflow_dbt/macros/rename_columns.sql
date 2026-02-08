{% macro rename_columns(mapping) %}
{% for old,new in mapping.items() %}
    {{old}} as {{new}}
    {% if not loop.last %}, {% endif %}
{% endfor %}
{% endmacro %}
