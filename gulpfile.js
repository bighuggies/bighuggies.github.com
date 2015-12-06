var http       = require('http'),
    express    = require('express'),
    path       = require('path'),
    spawn      = require('child_process').spawn,
    gulp       = require('gulp'),
    plumber    = require('gulp-plumber'),
    sourcemaps = require('gulp-sourcemaps'),
    rename     = require('gulp-rename'),
    less       = require('gulp-less'),
    cleancss   = require('gulp-minify-css'),
    livereload = require('gulp-livereload'),
    prefix     = require('gulp-autoprefixer'),
    notify     = require('gulp-notify');

gulp.task('less', function() {
    return gulp.src('less/main.less', {base: 'less'})
        .pipe(sourcemaps.init())
        .pipe(less())
        .pipe(prefix())
        .pipe(cleancss())
        .pipe(sourcemaps.write())
        .pipe(gulp.dest('css/'))
        .pipe(livereload());
});

gulp.task('jekyll', function() {
    jekyll = spawn('jekyll.bat', ['build', '--drafts', '--future']);

    jekyll.stdout.on('data', function (data) {
        console.log('jekyll:\t' + data); // works fine
    });
});

gulp.task('watch', ['build'], function() {
    livereload.listen();

    var reload = function(file) {
        livereload.changed(file.path);
    };

    gulp.watch('less/**', ['styles']);
    gulp.watch(['css/**', '_layouts/**', '_includes/**', 'blog/**', 'perdiem/**'], ['jekyll']);
    gulp.watch(['_site/**']).on('change', reload);
});

gulp.task('serve', function() {
    var app = express()
        .use(express.static(path.resolve('_site')));

    http.createServer(app).listen(4000);
});

gulp.task('styles', ['less']);

gulp.task('build', ['styles', 'jekyll']);
gulp.task('default', ['watch', 'serve']);
