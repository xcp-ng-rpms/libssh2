%global package_speccommit ac6700f896fa20478846d4ece85955c51592c320
%global usver 1.11.0
%global xsver 1
%global xsrel %{xsver}%{?xscount}%{?xshash}

Name:		libssh2
Version:	1.11.0
Release:	%{?xsrel}.1%{?dist}
Summary:	A library implementing the SSH2 protocol
License:	BSD-3-Clause
URL:		https://www.libssh2.org/
Source0: libssh2-1.11.0.tar.gz
Patch0: libssh2-1.11.0-strict-modes.patch
Patch1: libssh2-1.11.0-ssh-rsa-test.patch
Patch2: 0001-CP-50289-Remove-ssh-dss-key-type-from-tests.patch

# XCP-ng patches
Patch1000: libssh2-1.11.0-CVE-2026-58051-publickey-fix-potential-arbitrary-free-in-libssh2_pu.patch
Patch1001: libssh2-1.11.0-CVE-2026-66032-Prevent-dangling-pointer-by-nullifying-data-2180.patch
Patch1002: libssh2-1.11.0-CVE-2026-66035-transport-fix-potential-heap-overflow-on-ETM-decrypt.patch
Patch1003: libssh2-1.11.0-CVE-2026-66034-publickey-fix-potential-OOB-read-in-libssh2_publicke.patch
Patch1004: libssh2-1.11.0-CVE-2026-66033-openssl-fix-potential-OOB-read-write-with-AES-GCM-in.patch

BuildRequires:	coreutils
BuildRequires:	findutils
BuildRequires:	gcc
BuildRequires:	gnupg2
BuildRequires:	make
BuildRequires:	openssl-devel > 1:1.0.2
BuildRequires:	pkgconfig
BuildRequires:	sed
BuildRequires:	zlib-devel
BuildRequires:	/usr/bin/man

# Test suite requirements
# Full groff (not just groff-base) needed for the mansyntax check
BuildRequires:	groff
# We run the OpenSSH server and try to connect to it
BuildRequires:	openssh-server

%description
libssh2 is a library implementing the SSH2 protocol as defined by
Internet Drafts: SECSH-TRANS(22), SECSH-USERAUTH(25),
SECSH-CONNECTION(23), SECSH-ARCH(20), SECSH-FILEXFER(06)*,
SECSH-DHGEX(04), and SECSH-NUMBERS(10).

%package	devel
Summary:	Development files for libssh2
Requires:	%{name}%{?_isa} = %{version}-%{release}
Requires:	pkgconfig

%description	devel
The libssh2-devel package contains libraries and header files for
developing applications that use libssh2.

%package	docs
Summary:	Documentation for libssh2
Requires:	%{name} = %{version}-%{release}
BuildArch:	noarch

%description	docs
The libssh2-docs package contains man pages and examples for
developing applications that use libssh2.

%prep
%autosetup -p1 -n %{name}-%{version}

# Replace hard wired port number in the test suite to avoid collisions
# between 32-bit and 64-bit builds running on a single build-host
sed -i s/4711/47%{?__isa_bits}/ tests/{openssh_fixture.c,test_ssh{2.c,d.test}}

%build
# Test suite fails to compile if we use --disable-static
# https://github.com/libssh2/libssh2/issues/1056
%configure \
	--disable-silent-rules \
	--enable-shared \
	--disable-docker-tests
%{make_build}

%install
%{make_install} INSTALL="install -p"
find %{buildroot} -name '*.la' -delete

# Remove static library that we only built for testing
rm -v %{buildroot}%{_libdir}/libssh2.a

# Clean things up a bit for packaging
make -C example clean
find example/ -type f \
	'(' -name '*.am' -o -name '*.in' -o -name CMakeLists.txt ')' \
	-print -delete

# Remove redundant references to libdir in pkg-config file
sed -i	-e 's|-L%{_libdir} ||g' \
	-e 's|-L[$]{libdir} ||g' %{buildroot}%{_libdir}/pkgconfig/libssh2.pc

# Avoid multilib conflict on libssh2-devel
mv -v example example.%{_arch}

%check
LC_ALL=en_US.UTF-8 make -C tests check

%ldconfig_scriptlets

%files
%license COPYING
%doc docs/AUTHORS README RELEASE-NOTES
%{_libdir}/libssh2.so.1
%{_libdir}/libssh2.so.1.*

%files docs
%doc docs/BINDINGS.md docs/HACKING.md docs/TODO NEWS
%{_mandir}/man3/libssh2_*.3*

%files devel
%doc example.%{_arch}/
%{_includedir}/libssh2.h
%{_includedir}/libssh2_publickey.h
%{_includedir}/libssh2_sftp.h
%{_libdir}/libssh2.so
%{_libdir}/pkgconfig/libssh2.pc

%changelog
* Tue Nov 10 2026 Lucas Ravagnier <lucas.ravagnier@vates.tech> - 1.11.0-1.1
- Backport security fixes:
  CVE-2026-58051, CVE-2026-66032, CVE-2026-66033, CVE-2026-66034,
  CVE-2026-66035

* Thu Aug 22 2024 Deli Zhang <deli.zhang@citrix.com> - 1.11.0-1
- First imported release

