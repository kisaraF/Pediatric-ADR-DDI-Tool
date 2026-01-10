{% macro get_demo_primary_ids() %}

    {% set query %}
    select distinct primaryid
    from {{ ref('int__demo_base') }}
    where primaryid is not null
{% endset %}

    {% set results = run_query(query) %}

    {% if execute %}
        {% set results_list = results.columns[0].values() %}
    {% else %}
        {% set results_list = [] %}
    {% endif %}

    {{ return(results_list) }}

{% endmacro %}
