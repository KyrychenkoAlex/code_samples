import {Menu, SiderProps} from "antd";
import {BarChartOutlined, UserOutlined, CalendarOutlined} from "@ant-design/icons";
import React, {ForwardRefExoticComponent, RefAttributes} from "react";
import DashboardLayoutSiderStyle from "./DashboardLayoutSiderStyle";
import ScheduleSVG from "@/components/svg/ScheduleSVG";
import {useRouter} from "next/router";
import {localeContent} from "./locales";
import {useSelector} from "react-redux";
import {StateInterface} from "@/store/index";

interface DashboardLayoutSiderProps {
    collapsed: boolean,
    component: ForwardRefExoticComponent<SiderProps & RefAttributes<HTMLDivElement>>
}

const DashboardLayoutSider = (props: DashboardLayoutSiderProps) => {
    const {collapsed, component: Sider} = props;
    const {lang} = useSelector((state: StateInterface) => state.locale);
    const {push, route} = useRouter();
    const {dashboard, calendar, users} = localeContent[lang];
    const menuItems = [
        {
            key: '/dashboard',
            icon: <BarChartOutlined/>,
            label: dashboard
        },
        {
            key: '/dashboard/calendar',
            icon: <CalendarOutlined/>,
            label: calendar
        },
        {
            key: '/dashboard/users',
            icon: <UserOutlined/>,
            label: users
        }
    ];

    const onMenuClick = (menu) => {
        const {key} = menu;
        push(key, undefined, {shallow: true});
    };

    const activeItem = menuItems.find(item => {
        const exactMatch = route === item.key;
        const includeMatch = route.includes(item.key);


        return (exactMatch && !includeMatch) || (includeMatch && item.key !== '/dashboard');
    });


    return (
        <DashboardLayoutSiderStyle>
            <Sider trigger={null} collapsible collapsed={collapsed}>
                <div className={'logo'}>
                    <ScheduleSVG height={'50px'} width={'50px'}/>
                </div>
                <Menu
                    mode="inline"
                    defaultSelectedKeys={[activeItem?.key || route]}
                    items={menuItems}
                    onClick={onMenuClick}
                />
            </Sider>
        </DashboardLayoutSiderStyle>
    );
};

export default DashboardLayoutSider;