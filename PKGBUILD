# Author: Vitor Lopes <vmnlop@gmail.com>

pkgbase=('python-jade-application-kit')
pkgname=('python-jade-application-kit')
_module='Jade-Application-Kit'
pkgver=0.a25
pkgrel=1
pkgdesc="Build desktop applications using web technologies on Linux, with Python, JavaScript, HTML5, and CSS3 and webkit."
url="https://codesardine.github.io/Jade-Application-Kit"
depends=('python' 'python-gobject')
makedepends=('python-setuptools')
license=('GPL')
arch=('any')
source=("https://github.com/codesardine/Jade-Application-Kit/archive/master.zip")
md5sums=('SKIP')

pkgver() {
	cd "${srcdir}/Jade-Application-Kit-master"
	grep "version" setup.py | cut -d '"' -f2
}

build() {
    cd "${srcdir}/Jade-Application-Kit-master"
    python setup.py build
}

package() {
    depends+=()
    cd "${srcdir}/Jade-Application-Kit-master"
    python setup.py install --root="${pkgdir}" --optimize=1 --skip-build
}