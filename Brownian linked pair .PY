"""
ブラウン運動 v2 - 繋がった2点（異物）版
異物が熱運動の中で漂い、渦を生む

2点が結合して一緒に動く（剛体的な繋がり）
周囲のブラウン運動に影響を受けながら、独自の回転も持つ
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# Pisano 24方向テーブル
PISANO_24_DIRS = [
    (10, 0), (10, 3), (9, 5), (8, 7), (7, 8), (5, 9),
    (3, 10), (0, 10), (-3, 10), (-5, 9), (-7, 8), (-8, 7),
    (-10, 0), (-10, -3), (-9, -5), (-8, -7), (-7, -8), (-5, -9),
    (-3, -10), (0, -10), (3, -10), (5, -9), (7, -8), (8, -7),
]

print("=== Brownian Motion v2 - Connected Pair ===")
print("繋がった2点が熱運動の中で漂う")
print("異物感の可視化\n")


class LinkedParticlePair:
    """繋がった2点の粒子ペア"""
    def __init__(self, x1, y1, x2, y2, mass=20):
        self.x1, self.y1 = float(x1), float(y1)  # 粒子1の座標
        self.x2, self.y2 = float(x2), float(y2)  # 粒子2の座標
        self.vx, self.vy = 0.0, 0.0  # 重心の速度
        self.angular_velocity = 0.0  # 回転速度
        self.mass = mass  # 質量（慣性）
        
    def get_center(self):
        """重心を計算"""
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return cx, cy
    
    def apply_force(self, fx, fy):
        """力を加える（足し算）"""
        self.vx += fx / self.mass
        self.vy += fy / self.mass
    
    def apply_torque(self, torque):
        """トルク（回転力）を加える"""
        self.angular_velocity += torque / (self.mass * 2)
    
    def update_position(self):
        """位置を更新"""
        # 重心の移動
        cx, cy = self.get_center()
        cx += self.vx
        cy += self.vy
        
        # 2点間の距離を保ったまま回転
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        distance = np.sqrt(dx**2 + dy**2)
        
        # 現在の角度
        angle = np.arctan2(dy, dx)
        angle += self.angular_velocity
        
        # 新しい位置（重心から等距離）
        half_dist = distance / 2
        self.x1 = cx - half_dist * np.cos(angle)
        self.y1 = cy - half_dist * np.sin(angle)
        self.x2 = cx + half_dist * np.cos(angle)
        self.y2 = cy + half_dist * np.sin(angle)
        
        # 摩擦（減衰）
        self.vx *= 0.95
        self.vy *= 0.95
        self.angular_velocity *= 0.98


class BrownianWithLinkedPair:
    def __init__(self, width=80, height=40, temperature=5):
        self.width = width
        self.height = height
        self.temperature = temperature
        
        # 速度場（背景の流体）
        self.vx = np.zeros((height, width), dtype=np.float32)
        self.vy = np.zeros((height, width), dtype=np.float32)
        
        # 密度場
        self.density = np.ones((height, width), dtype=np.float32) * 0.5
        
        # 繋がった2点の粒子ペア（異物）
        center_x, center_y = width // 2, height // 2
        self.linked_pair = LinkedParticlePair(
            x1=center_x - 2, y1=center_y,
            x2=center_x + 2, y2=center_y,
            mass=30
        )
        
        self.step = 0
        
    def apply_thermal_motion(self):
        """背景流体の熱運動"""
        for y in range(self.height):
            for x in range(self.width):
                # ランダムなPisano方向にキック
                random_dir = np.random.randint(0, 24)
                dx, dy = PISANO_24_DIRS[random_dir]
                
                kick_strength = self.temperature
                self.vx[y, x] += (dx * kick_strength) // 20
                self.vy[y, x] += (dy * kick_strength) // 20
    
    def update_linked_pair(self):
        """繋がった2点の更新"""
        # 周囲の流体から力を受ける
        cx, cy = self.linked_pair.get_center()
        ix, iy = int(cx), int(cy)
        
        if 0 <= ix < self.width and 0 <= iy < self.height:
            # 周囲の流体速度を平均
            fx = fy = 0
            count = 0
            for dy in range(-2, 3):
                for dx in range(-2, 3):
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        fx += self.vx[ny, nx]
                        fy += self.vy[ny, nx]
                        count += 1
            
            if count > 0:
                fx /= count
                fy /= count
                self.linked_pair.apply_force(fx / 10, fy / 10)
        
        # ランダムなトルク（熱揺らぎによる回転）
        random_torque = (np.random.random() - 0.5) * self.temperature / 10
        self.linked_pair.apply_torque(random_torque)
        
        # 位置更新
        self.linked_pair.update_position()
        
        # 2点の位置に密度を追加（異物の可視化）
        x1, y1 = int(self.linked_pair.x1), int(self.linked_pair.y1)
        x2, y2 = int(self.linked_pair.x2), int(self.linked_pair.y2)
        
        if 0 <= x1 < self.width and 0 <= y1 < self.height:
            self.density[y1, x1] += 5.0
        if 0 <= x2 < self.width and 0 <= y2 < self.height:
            self.density[y2, x2] += 5.0
        
        # 繋がった2点が流体に影響を与える（双方向結合）
        for px, py in [(x1, y1), (x2, y2)]:
            if 0 <= px < self.width and 0 <= py < self.height:
                # 異物の速度を周囲に伝播
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.vx[ny, nx] += self.linked_pair.vx / 8
                            self.vy[ny, nx] += self.linked_pair.vy / 8
    
    def propagate_fluid(self):
        """流体の拡散と伝播"""
        new_vx = np.copy(self.vx)
        new_vy = np.copy(self.vy)
        new_density = np.copy(self.density)
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
                # 周囲8方向から影響を集計
                influences_x = 0
                influences_y = 0
                influences_d = 0
                count = 0
                
                for dy_offset in [-1, 0, 1]:
                    for dx_offset in [-1, 0, 1]:
                        if dy_offset == 0 and dx_offset == 0:
                            continue
                        
                        ny = y + dy_offset
                        nx = x + dx_offset
                        
                        if 0 <= ny < self.height and 0 <= nx < self.width:
                            influences_x += self.vx[ny, nx]
                            influences_y += self.vy[ny, nx]
                            influences_d += self.density[ny, nx]
                            count += 1
                
                if count > 0:
                    avg_vx = influences_x / count
                    avg_vy = influences_y / count
                    avg_d = influences_d / count
                    
                    # Pisano方向の影響
                    current_vx = self.vx[y, x]
                    current_vy = self.vy[y, x]
                    speed = int(np.sqrt(current_vx**2 + current_vy**2))
                    
                    if speed > 0:
                        angle_index = int((np.arctan2(current_vy, current_vx) * 24 / (2 * np.pi)) % 24)
                    else:
                        angle_index = np.random.randint(0, 24)
                    
                    pisano_shift = (angle_index + self.step) % 24
                    dir_dx, dir_dy = PISANO_24_DIRS[pisano_shift]
                    
                    # 新しい値（足し算 + 摩擦）
                    new_vx[y, x] = (current_vx * 6 + avg_vx * 3 + dir_dx / 10 - 1) / 9
                    new_vy[y, x] = (current_vy * 6 + avg_vy * 3 + dir_dy / 10 - 1) / 9
                    new_density[y, x] = (self.density[y, x] * 7 + avg_d * 3) / 10
        
        self.vx = new_vx
        self.vy = new_vy
        self.density = new_density * 0.98  # 密度の緩やかな減衰
        self.step += 1
    
    def step_simulation(self):
        """1ステップ実行"""
        self.apply_thermal_motion()
        self.update_linked_pair()
        self.propagate_fluid()
    
    def get_visualization_data(self):
        skip = 3
        X, Y = np.meshgrid(np.arange(0, self.width, skip), 
                          np.arange(0, self.height, skip))
        U = self.vx[::skip, ::skip]
        V = self.vy[::skip, ::skip]
        D = self.density[::skip, ::skip]
        return X, Y, U, V, D


# ============================================
# 実行部分
# ============================================
if __name__ == "__main__":
    print("温度設定: 5")
    print("繋がった2点の質量: 30")
    print("異物が漂い始めます...\n")
    
    sim = BrownianWithLinkedPair(width=80, height=40, temperature=5)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # 軌跡記録
    trajectory_x = []
    trajectory_y = []
    
    def update(frame):
        ax.clear()
        
        # シミュレーション1ステップ
        sim.step_simulation()
        
        # 軌跡記録
        cx, cy = sim.linked_pair.get_center()
        trajectory_x.append(cx)
        trajectory_y.append(cy)
        
        # 可視化
        X, Y, U, V, D = sim.get_visualization_data()
        
        extent = [0, sim.width, 0, sim.height]
        
        # 密度を背景として表示
        im = ax.imshow(sim.density, extent=extent, origin='lower', 
                       cmap='hot', alpha=0.7, aspect='auto', vmin=0, vmax=8)
        
        # 速度ベクトル
        speed = np.sqrt(U**2 + V**2)
        if np.max(speed) > 0:
            ax.quiver(X, Y, U, V, speed, cmap='cool', scale=500, width=0.002, alpha=0.5)
        
        # 繋がった2点を描画（異物）
        x1, y1 = sim.linked_pair.x1, sim.linked_pair.y1
        x2, y2 = sim.linked_pair.x2, sim.linked_pair.y2
        
        # 2点を線で繋ぐ
        ax.plot([x1, x2], [y1, y2], 'w-', linewidth=3, alpha=0.9)
        ax.plot([x1, x2], [y1, y2], 'yo', markersize=8, markeredgecolor='red', markeredgewidth=2)
        
        # 軌跡を表示
        if len(trajectory_x) > 1:
            ax.plot(trajectory_x[-50:], trajectory_y[-50:], 'c-', linewidth=1.5, alpha=0.6)
        
        ax.set_title(f'Brownian Motion - Linked Pair Drifting - Step {frame}', fontsize=14)
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_xlim(0, sim.width)
        ax.set_ylim(0, sim.height)
        
        # 統計情報
        pair_speed = np.sqrt(sim.linked_pair.vx**2 + sim.linked_pair.vy**2)
        ax.text(5, sim.height - 5, 
                f'Pair Speed: {pair_speed:.2f} | Angular Vel: {sim.linked_pair.angular_velocity:.3f}', 
                color='white', fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        return ax,
    
    # アニメーション作成
    anim = animation.FuncAnimation(fig, update, frames=200, interval=80, blit=False)
    
    output_path = 'brownian_linked_pair.gif'
    anim.save(output_path, writer='pillow', fps=12)
    print(f"\nアニメーション保存: {output_path}")
    
    plt.close()
    
    # 最終状態 + 軌跡
    fig, ax = plt.subplots(figsize=(14, 7))
    
    X, Y, U, V, D = sim.get_visualization_data()
    extent = [0, sim.width, 0, sim.height]
    im = ax.imshow(sim.density, extent=extent, origin='lower', 
                   cmap='hot', alpha=0.7, aspect='auto')
    speed = np.sqrt(U**2 + V**2)
    ax.quiver(X, Y, U, V, speed, cmap='cool', scale=500, width=0.002, alpha=0.5)
    
    # 全軌跡を表示
    ax.plot(trajectory_x, trajectory_y, 'c-', linewidth=2, alpha=0.8, label='Trajectory')
    
    # 最終位置
    x1, y1 = sim.linked_pair.x1, sim.linked_pair.y1
    x2, y2 = sim.linked_pair.x2, sim.linked_pair.y2
    ax.plot([x1, x2], [y1, y2], 'w-', linewidth=3)
    ax.plot([x1, x2], [y1, y2], 'yo', markersize=10, markeredgecolor='red', markeredgewidth=2)
    
    ax.set_title(f'Final State with Full Trajectory (Step {sim.step})', fontsize=14)
    ax.legend(loc='upper right')
    
    static_path = 'brownian_linked_final.png'
    plt.savefig(static_path, dpi=150, bbox_inches='tight')
    print(f"最終状態保存: {static_path}")
    
    plt.close()
    
    print("\n=== Linked Pair Brownian Complete ===")
    print(f"総ステップ数: {sim.step}")
    final_cx, final_cy = sim.linked_pair.get_center()
    print(f"最終重心位置: ({final_cx:.2f}, {final_cy:.2f})")
    print(f"移動距離: {np.sqrt((final_cx - sim.width/2)**2 + (final_cy - sim.height/2)**2):.2f}")
    print("\n異物が熱運動の中で漂い、渦を生む様子を観察完了")
