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
                        $municipio.val(data.informacion_completa.municipio || '');
                        $estado.val(data.informacion_completa.estado || '');
                        $pais.val(data.informacion_completa.pais || '');
                    } else if (data.colonias && data.colonias.length > 0) {
                        var options = '';
                        data.colonias.forEach(function(col) {
                            options += '<option value="' + col.nombre + '" data-municipio="' + (col.municipio_nombre || '') + '" data-estado="' + (col.estado_nombre || '') + '" data-pais="' + (col.pais_nombre || '') + '">' + col.nombre + '</option>';
                        });
                        $colonia.html(options);
                        // Autocompletar municipio/estado/pais con la primera colonia
                        var first = data.colonias[0];
                        $municipio.val(first.municipio_nombre || '');
                        $estado.val(first.estado_nombre || '');
                        $pais.val(first.pais_nombre || '');
                    }
                }
            });
        });

        $colonia.on('change', function() {
            var $selected = $(this).find('option:selected');
            $municipio.val($selected.data('municipio') || '');
            $estado.val($selected.data('estado') || '');
            $pais.val($selected.data('pais') || '');
        });
    });
})(django.jQuery);