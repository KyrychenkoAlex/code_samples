import styled from "styled-components";

export default styled.div`
  .ant-layout {
    min-height: 100vh;
  }

  .ant-menu {
    background: ${({theme}) => theme.colors.primaryBackground};
    color: ${({theme}) => theme.colors.primaryTextColor};
  }

  .ant-layout-content {
    min-height: calc(100vh - ${({theme}) => theme.sizes.headerHeight});
  }
`;