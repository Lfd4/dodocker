FROM {{ t.imagename }}

{% if t.imagename == 'scratch' %}
ADD scratch.txt /output.txt
{% endif %}

{% if t.imagename == 'busybox' %}
ADD busybox.txt /output.txt
{% endif %}

ADD someotherfile.txt /
