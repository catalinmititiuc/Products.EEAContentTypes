/**
 */

(function() {
    tinymce.create('tinymce.plugins.EEAEmbedPlugin', {
        init : function(ed, url) {
            // Register commands
            ed.addCommand('mceEEAEmbed', function() {
                // Internal image object like a flash placeholder
                if (ed.dom.getAttrib(ed.selection.getNode(), 'class').indexOf('mceItem') != -1)
                    return;

                ed.windowManager.open({
                    file : url + '/ploneimage.htm',
                    width : 846 + parseInt(ed.getLang('ploneimage.delta_width', 0)),
                    height : 550 + parseInt(ed.getLang('ploneimage.delta_height', 0)),
                    inline : 1
                }, {
                    plugin_url : url
                });
            });

            // Register buttons
            ed.addButton('eeaembed', {
                title : 'Add Embed',
                cmd : 'mceEEAEmbed'
            });
        },

        getInfo : function() {
            return {
                longname : 'Plone Embed Content',
                author : 'David Ichim',
                authorurl : '',
                infourl : '',
                version : tinymce.majorVersion + "." + tinymce.minorVersion
            };
        }
    });

    // Register plugin
    tinymce.PluginManager.add('eeaembed', tinymce.plugins.EEAEmbedPlugin);
})();
