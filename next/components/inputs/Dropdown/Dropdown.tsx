import {Dropdown as AntdDropdown, Menu} from "antd";
import DropdownStyles from "./DropdownStyles";
import React from "react";

interface DropdownInterface {
    menuItems: Array<any>;
    children: React.ReactNode
}

const Dropdown = (props: DropdownInterface) => {
    const menu = (
        <DropdownStyles>
            <Menu
                className={'menu-block'}
                items={props.menuItems}
            />
        </DropdownStyles>
    );
    return (
        <AntdDropdown overlay={menu} trigger={['click']}>
            {props.children}
        </AntdDropdown>
    );
};

export default Dropdown;