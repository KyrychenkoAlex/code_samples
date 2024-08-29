import styled from "styled-components";

export default styled.div`
  .logo {
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 20px;

    .schedule-icon {
      min-width: 50px;
    }
  }

  .ant-layout-sider {
    height: 100%;
    background: ${({theme}) => theme.colors.primaryBackground};
    color: ${({theme}) => theme.colors.primaryTextColor};
  }
`;