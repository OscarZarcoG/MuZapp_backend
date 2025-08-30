(function($) {
    $(document).ready(function() {
        var $cp = $('#id_codigo_postal');
        var $colonia = $('#id_colonia');
        var $municipio = $('#id_municipio');
        var $estado = $('#id_estado');
        var $pais = $('#id_pais');

        function limpiarCampos() {
            $colonia.empty();
            $municipio.val('');
            $estado.val('');
            $pais.val('');
        }

        function setIfEmpty($field, value) {
            if (!$field.val()) {
                $field.val(value || '');
            }
        }

        $cp.on('change', function() {
            var cp = $(this).val();
            if (!cp) return limpiarCampos();
            limpiarCampos();
            $.ajax({
                url: '/api/mexico/codigo-postal/' + cp + '/',
                method: 'GET',
                success: function(data) {
                    if (data.informacion_completa) {
                        $colonia.html('<option value="' + data.informacion_completa.colonia + '">' + data.informacion_completa.colonia + '</option>');
                        setIfEmpty($municipio, data.informacion_completa.municipio);
                        setIfEmpty($estado, data.informacion_completa.estado);
                        setIfEmpty($pais, data.informacion_completa.pais);
                    } else if (data.colonias && data.colonias.length > 0) {
                        var options = '';
                        data.colonias.forEach(function(col) {
                            options += '<option value="' + col.nombre + '" data-municipio="' + (col.municipio_nombre || '') + '" data-estado="' + (col.estado_nombre || '') + '" data-pais="' + (col.pais_nombre || '') + '">' + col.nombre + '</option>';
                        });
                        $colonia.html(options);
                        // Always replace information when postal code changes
                        setIfEmpty($municipio, data.colonias[0].municipio_nombre);
                        setIfEmpty($estado, data.colonias[0].estado_nombre);
                        setIfEmpty($pais, data.colonias[0].pais_nombre);
                    } else {
                        limpiarCampos();
                    }
                }
            });
        });

        $colonia.on('change', function() {
            var $selected = $(this).find('option:selected');
            setIfEmpty($municipio, $selected.data('municipio'));
            setIfEmpty($estado, $selected.data('estado'));
            setIfEmpty($pais, $selected.data('pais'));
        });
    });
})(django.jQuery);