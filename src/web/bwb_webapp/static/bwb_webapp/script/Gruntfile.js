/**
 * Defines all tasks used in this project
 * Execute by typing "grunt" into the console
 * @param  {Object} grunt The grunt.js namespace
 */
module.exports = function(grunt)
{

    // Project configuration.
    grunt.initConfig({

        pkg: grunt.file.readJSON('package.json'),

        //-------------------------------------------------------------------------

        settings: {
            projectId: "surfaceBeam",
            srcDir: "src",
            distDir: "script",
            copyright: "Benjamin Haettasch",
            author: "Benjamin Haettasch",
            changed: grunt.template.today("yyyy-mm-dd HH:MM")
        },


        //-------------------------------------------------------------------------

        ts: {
            options: {                    // use to override the default options, see : http://gruntjs.com/configuring-tasks#options
                target: 'es5',            // es3 (default) / or es5
                module: 'amd',
                sourceMap: true,
                declaration: true,        //create a d.ts file
                comments: false,
                noImplicitAny: true,
                suppressImplicitAnyIndexErrors: true
            },
            default: {
                src: ["./ts_src/**/*.ts", "!./node_modules/**/*.ts", "!./dist/*"],       // The source typescript files
                reference: "ts_src/reference.ts",
                out: 'dist/bwb.js'
            }
        }

        //-------------------------------------------------------------------------
    })


    //load npm tasks
    grunt.loadNpmTasks("grunt-ts");

    //register grunt tasks
    grunt.registerTask('build', ['ts:default']);
    grunt.registerTask('default', ['build']);
};
