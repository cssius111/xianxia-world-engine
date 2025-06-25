// e2e_create_character.spec.js
// 使用 Cypress 编写的端到端测试，用于验证角色创建流程

/*
步骤：
1. 访问 /start 页面，输入角色姓名
2. 点击“随机生成”让系统自动分配属性
3. 点击“确认创建”
4. 通过请求 /status 接口获取当前角色数据
5. 对比侧边栏生命与灵力数值是否与 /status 返回一致
6. 再次在 /start?mode=dev 流程中创建角色，确保可以手动修改属性值
*/

describe('角色创建流程', () => {
  it('随机创建角色并校验状态栏', () => {
    cy.visit('/start');
    cy.get('#characterName').type('测试角色');
    cy.contains('button', '随机生成').click();
    cy.contains('button', '确认创建').click();

    cy.request('/status').then((resp) => {
      const attrs = resp.body.player.attributes;
      cy.get('#healthText').should('contain', `${attrs.current_health}/${attrs.max_health}`);
      cy.get('#manaText').should('contain', `${attrs.current_mana}/${attrs.max_mana}`);
    });
  });

  it('开发模式允许手动修改属性', () => {
    cy.visit('/start?mode=dev');
    cy.get('#characterName').type('开发模式');

    // 假设在开发模式下属性值可通过调节按钮修改
    cy.get('#attrConstitution').invoke('text', '9');
    cy.get('#attrSpirit').invoke('text', '8');

    cy.contains('button', '确认创建').click();

    cy.request('/status').its('body.player.attributes').should((attrs) => {
      expect(attrs.constitution).to.eq(9);
      expect(attrs.spirit).to.eq(8);
    });
  });
});
