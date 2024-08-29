import styled from "styled-components";

export default styled.div`
  .menu-block {
    border: 1px solid #cce0fa;
    border-radius: 5px;
  }

  .disabled-item {
    &:hover {
      background: transparent;
      pointer-events: none;
    }
  }
`;