import styled from "styled-components";

export default styled.div`

  .ant-layout-header {
    background: ${({theme}) => theme.colors.primaryBackground};
    color: ${({theme}) => theme.colors.primaryTextColor};
    height: ${({theme}) => theme.sizes.headerHeight};
  }

  .trigger {
    padding: 20px;
    font-size: 20px;
  }

  .user-avatar {
    background-color: ${({theme}) => theme.colors.avatarBackground};
  }

  .avatar-block {
    margin-right: 10px;
    cursor: pointer;
    float: right;
    display: flex;
    justify-content: center;
    align-items: center;

    .fullname {
      margin-right: 5px;
    }
  }
`;