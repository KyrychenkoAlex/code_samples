"use client"

import { useTransition } from "react";
import { useLocale } from 'next-intl';
import { Select } from "antd";

import {useRouter, usePathname} from '@/navigation';
import {locales, localeNames} from '@/i18nconfig';

export default function LocaleSwitcher() {
  const router = useRouter();
  const pathname = usePathname();

  const [isPending, startTransition] = useTransition();

  const defaultLocale = useLocale();

  const handleChange = (value: string) => {
    startTransition(() => {
      router.replace(pathname, {locale: value});
    });
  }

  const options = locales.map((locale) => ({
    value: locale,
    label: localeNames[locale],
  }))

  return (
    <Select
      defaultValue={defaultLocale}
      loading={isPending}
      style={{ width: 120 }}
      onChange={handleChange}
      options={options}
    />
  )
}
