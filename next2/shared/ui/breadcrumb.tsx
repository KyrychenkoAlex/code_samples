"use client"

import { useMemo } from "react";
import Link from "next/link";
import {upperFirst} from 'lodash'
import { Breadcrumb as BreadcrumbAntD } from 'antd';
import { usePathname } from "next/navigation";

function Breadcrumb() {

  const pathname = usePathname();

  const breadcrumbItems = useMemo(() => {
    if (!pathname) {
      return [];
    }

    const parts = pathname.split("/").filter(Boolean);

    const paths = [];

    let path = '';

    for (let i = 0; i < parts.length; i++) {
      path += '/' + parts[i];
      paths.push({
        title: upperFirst(parts[i]),
        path
      });
    }

    return paths.map((path, index) => ({
      title: index === parts.length - 1 ? path.title : <Link href={path.path}>{path.title}</Link>
    }));
  }, [pathname])

  return (
    <BreadcrumbAntD
      style={{ marginBottom: '16px' }}
      items={breadcrumbItems}
    />
  )
}

export default Breadcrumb;
