{% macro clean_string(column_name) %}
    -- 1. Convert to lower case and trim whitespace
    -- 2. Remove punctuations (anything not a word character or space)
    -- 3. Replace one or more whitespaces with a single underscore
    
    regexp_replace(
        regexp_replace(
            lower(trim({{ column_name }})), 
            '[^\\w\\s]', ''  -- Remove punctuations
        ), 
        '\\s+', '_'        -- Replace whitespace with underscore
    )
{% endmacro %}
