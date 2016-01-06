%{?scl:%scl_package mockito}
%{!?scl:%global pkg_name %{name}}
%{?java_common_find_provides_and_requires}

Name:           %{?scl_prefix}mockito
Version:        1.9.0
Release:        16%{?dist}
Summary:        A Java mocking framework

License:        MIT
URL:            http://code.google.com/p/mockito/
Source0:        mockito-%{version}.tar.xz
Source1:        make-mockito-sourcetarball.sh
Patch0:         fixup-ant-script.patch
Patch1:         fix-cglib-refs.patch
Patch2:         maven-cglib-dependency.patch
Patch3:         fix-bnd-config.patch
Patch4:         %{pkg_name}-matcher.patch
# Workaround for NPE in setting NamingPolicy in cglib
Patch5:         setting-naming-policy.patch

BuildArch:      noarch
BuildRequires:  java-devel
BuildRequires:  %{?scl_prefix_java_common}ant
BuildRequires:  %{?scl_prefix_java_common}objenesis
BuildRequires:  %{?scl_prefix_java_common}cglib
BuildRequires:  %{?scl_prefix_java_common}junit
BuildRequires:  %{?scl_prefix_java_common}hamcrest
BuildRequires:  %{?scl_prefix_maven}aqute-bnd

Requires:       %{?scl_prefix_java_common}objenesis
Requires:       %{?scl_prefix_java_common}cglib
Requires:       %{?scl_prefix_java_common}junit
Requires:       %{?scl_prefix_java_common}hamcrest

%description
Mockito is a mocking framework that tastes really good. It lets you write
beautiful tests with clean & simple API. Mockito doesn't give you hangover
because the tests are very readable and they produce clean verification
errors.

%package javadoc
Summary:        Javadocs for %{pkg_name}
Group:          Documentation
Requires:       jpackage-utils

%description javadoc
This package contains the API documentation for %{pkg_name}.

%prep
%setup -q -n %{pkg_name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1
# Set Bundle-Version properly
sed -i 's/Bundle-Version= ${version}/Bundle-Version= %{version}/' conf/mockito-core.bnd
%patch3
%patch4 -p1
%patch5 -p1

%build
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
build-jar-repository -p lib/compile objenesis cglib junit hamcrest/core
unset ANT_HOME
ant jar javadoc
# Convert to OSGi bundle
pushd target
java -jar $(build-classpath aqute-bnd) wrap -output mockito-core-%{version}.bar -properties ../conf/mockito-core.bnd mockito-core-%{version}.jar
popd
%{?scl:EOF}

%install
%{?scl:scl enable %{scl_maven} %{scl} - << "EOF"}
mkdir -p $RPM_BUILD_ROOT%{_javadir}
sed -i -e "s|@version@|%{version}|g" maven/mockito-core.pom
cp -p target/mockito-core-%{version}.bar $RPM_BUILD_ROOT%{_javadir}/%{pkg_name}.jar

install -d -m 755 $RPM_BUILD_ROOT%{_mavenpomdir}
install -pm 644 maven/mockito-core.pom  \
        $RPM_BUILD_ROOT%{_mavenpomdir}/JPP-%{pkg_name}.pom

mkdir -p $RPM_BUILD_ROOT%{_javadocdir}/%{pkg_name}
cp -rp target/javadoc/* $RPM_BUILD_ROOT%{_javadocdir}/%{pkg_name}

%add_maven_depmap JPP-%{pkg_name}.pom %{pkg_name}.jar -a "org.mockito:mockito-all"
%{?scl:EOF}

%files -f .mfiles
%{_javadir}/%{pkg_name}.jar
%{_mavenpomdir}/JPP-%{pkg_name}.pom
%doc NOTICE
%doc LICENSE

%files javadoc
%{_javadocdir}/%{pkg_name}
%doc LICENSE
%doc NOTICE

%changelog
* Mon May 11 2015 Mat Booth <mat.booth@redhat.com> - 1.9.0-16
- Resolves: rhbz#1219013 - Fails to build from source

* Fri Mar 28 2014 Michael Simacek <msimacek@redhat.com> - 1.9.0-15
- Use Requires: java-headless rebuild (#1067528)

* Wed Dec 11 2013 Michael Simacek <msimacek@redhat.com> - 1.9.0-14
- Workaround for NPE in setting NamingPolicy

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-13
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Mon Mar 25 2013 Tomas Radej <tradej@redhat.com> - 1.9.0-12
- Patched LocalizedMatcher due to hamcrest update, (bug upstream)

* Thu Feb 14 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-11
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Thu Sep 6 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.9.0-10
- More Import-Package fixes. Note that fix-cglib-refs.patch is
  not suitable for upstream:
  http://code.google.com/p/mockito/issues/detail?id=373

* Tue Sep 4 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.9.0-9
- Fix missing Import-Package in manifest.

* Mon Aug 27 2012 Severin Gehwolf <sgehwolf@redhat.com> 1.9.0-8
- Add aqute bnd instructions for OSGi metadata

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.9.0-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Mon Apr 30 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-6
- Place JavaDoc in directly under %{_javadocdir}/%{name} instead
  of %{_javadocdir}/%{name}/javadoc

* Wed Apr 25 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-5
- Removed post/postun hook for update_maven_depmap

* Tue Apr 24 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-4
- Fix groupId of cglib dependency
- Add additional depmap for mockito-all
- Update depmap on post and postun
- Fix version in pom

* Wed Feb 22 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-3
- Added cglib dependency to pom

* Tue Feb 21 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-2
- Include upstream Maven pom.xml in package
- Added missing Requires for cglib, junit4, hamcrest, objenesis
- Added source tarball generating script to sources

* Thu Feb 16 2012 Roman Kennke <rkennke@redhat.com> 1.9.0-1
- Initial package
