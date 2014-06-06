var http       = require('http'),
    connect    = require('connect'),
    path       = require('path'),
    spawn      = require('child_process').spawn,
    gulp       = require('gulp'),
    plumber    = require('gulp-plumber'),
    less       = require('gulp-less'),
    livereload = require('gulp-livereload'),
    prefix     = require('gulp-autoprefixer'),
    notify     = require('gulp-notify');

gulp.task('styles', function() {
    var styles = gulp.src('less/main.less')
        .pipe(plumber())
        .pipe(less({"compress": true}))
        .pipe(prefix())
        .pipe(gulp.dest('css/'));

    return styles;
});

gulp.task('jekyll', function() {
    jekyll = spawn('jekyll.bat', ['build', '--drafts', '--future']);

    jekyll.stdout.on('data', function (data) {
        console.log('jekyll:\t' + data); // works fine
    });
});

gulp.task('watch', function() {
    var server = livereload();

    var reload = function(file) {
        server.changed(file.path);
    };

    gulp.watch('less/**', ['styles']);
    gulp.watch(['css/**', '_layouts/**', '_includes/**', 'blog/**'], ['jekyll']);
    gulp.watch(['_site/**']).on('change', reload);
});

gulp.task('serve', function() {
    var app = connect()
        .use(connect.logger('dev'))
        .use(connect.static(path.resolve('_site')));

    http.createServer(app).listen(4000);
});

gulp.task('build', ['styles', 'jekyll']);
gulp.task('default', ['watch', 'serve']);