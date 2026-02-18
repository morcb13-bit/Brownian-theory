 """
ブラウン運動 v3 - もっと漂う感じ
異物が軽くなり、ゆらゆらと漂う

調整ポイント：
- 質量を減らす（軽くして流れに乗りやすく）
- 摩擦を減らす（慣性で漂う）
- 流体の影響を強める
- 回転の減衰を緩やかに
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

print("=== Brownian Motion v3 - More Drifting ===")
print("より軽く、よりゆらゆら漂う異物")
print("流れに乗る感じを強調\n")


class LightLinkedPair:
    """軽く漂う繋がった2点"""
    def __init__(self, x1, y1, x2, y2, mass=8):  # 質量を軽く
        self.x1, self.y1 = float(x1), float(y1)
        self.x2, self.y2 = float(x2), float(y2)
        self.vx, self.vy = 0.0, 0.0
        self.angular_velocity = 0.0
        self.mass = mass  # 以前の30から8に軽量化
        
    def get_center(self):
        cx = (self.x1 + self.x2) / 2
        cy = (self.y1 + self.y2) / 2
        return cx, cy
    
    def apply_force(self, fx, fy):
        """力を加える（軽いので大きく動く）"""
        self.vx += fx / self.mass
        self.vy += fy / self.mass
    
    def apply_torque(self, torque):
        """トルクを加える"""
        self.angular_velocity += torque / (self.mass * 1.5)  # 回りやすく
    
    def update_position(self, bounds_width, bounds_height):
        """位置を更新（境界を超えたら反射）"""
        # 重心の移動
        cx, cy = self.get_center()
        cx += self.vx
        cy += self.vy
        
        # 境界チェック（壁で反射）
        if cx < 5 or cx > bounds_width - 5:
            self.vx *= -0.8
            cx = np.clip(cx, 5, bounds_width - 5)
        if cy < 5 or cy > bounds_height - 5:
            self.vy *= -0.8
            cy = np.clip(cy, 5, bounds_height - 5)
        
        # 2点間の距離を保ったまま回転
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        distance = np.sqrt(dx**2 + dy**2)
        
        angle = np.arctan2(dy, dx)
        angle += self.angular_velocity
        
        half_dist = distance / 2
        self.x1 = cx - half_dist * np.cos(angle)
        self.y1 = cy - half_dist * np.sin(angle)
        self.x2 = cx + half_dist * np.cos(angle)
        self.y2 = cy + half_dist * np.sin(angle)
        
        # 摩擦（減衰）を緩やかに
        self.vx *= 0.98  # 0.95から0.98に（慣性が残りやすい）
        self.vy *= 0.98
        self.angular_velocity *= 0.99  # 0.98から0.99に（回転が持続しやすい）


class DriftingBrownian:
    def __init__(self, width=80, height=40, temperature=7):  # 温度を上げる
        self.width = width
        self.height = height
        self.temperature = temperature
        
        # 速度場
        self.vx = np.zeros((height, width), dtype=np.float32)
        self.vy = np.zeros((height, width), dtype=np.float32)
        
        # 密度場（初期状態を少し分散）
        self.density = np.ones((height, width), dtype=np.float32) * 0.3
        
        # 軽い繋がった2点
        center_x, center_y = width // 2, height // 2
        self.linked_pair = LightLinkedPair(
            x1=center_x - 2, y1=center_y,
            x2=center_x + 2, y2=center_y,
            mass=8  # 軽量化
        )
        
        # 初期速度を与える（少し動き出した状態）
        self.linked_pair.vx = 2.0
        self.linked_pair.vy = 1.0
        
        self.step = 0
        
    def apply_thermal_motion(self):
        """背景流体の熱運動（強め）"""
        for y in range(self.height):
            for x in range(self.width):
                # ランダムなPisano方向
                random_dir = np.random.randint(0, 24)
                dx, dy = PISANO_24_DIRS[random_dir]
                
                # キックを強めに
                kick_strength = self.temperature
                self.vx[y, x] += (dx * kick_strength) // 15  # 20から15に
                self.vy[y, x] += (dy * kick_strength) // 15
    
    def update_linked_pair(self):
        """繋がった2点の更新"""
        cx, cy = self.linked_pair.get_center()
        ix, iy = int(cx), int(cy)
        
        if 0 <= ix < self.width and 0 <= iy < self.height:
            # 周囲の流体速度を広範囲から集める（3x3から5x5へ）
            fx = fy = 0
            count = 0
            for dy in range(-3, 4):  # -2から-3に拡大
                for dx in range(-3, 4):
                    nx, ny = ix + dx, iy + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        fx += self.vx[ny, nx]
                        fy += self.vy[ny, nx]
                        count += 1
            
            if count > 0:
                fx /= count
                fy /= count
                # 流体の影響を強める（10から5へ）
                self.linked_pair.apply_force(fx / 5, fy / 5)
        
        # ランダムなトルク（揺らぎ）を強めに
        random_torque = (np.random.random() - 0.5) * self.temperature / 5  # 10から5へ
        self.linked_pair.apply_torque(random_torque)
        
        # 位置更新
        self.linked_pair.update_position(self.width, self.height)
        
        # 2点の位置に密度を追加
        x1, y1 = int(self.linked_pair.x1), int(self.linked_pair.y1)
        x2, y2 = int(self.linked_pair.x2), int(self.linked_pair.y2)
        
        if 0 <= x1 < self.width and 0 <= y1 < self.height:
            self.density[y1, x1] += 3.0  # 5から3へ（薄めに）
        if 0 <= x2 < self.width and 0 <= y2 < self.height:
            self.density[y2, x2] += 3.0
        
        # 異物が流体に与える影響を弱める（より受動的に）
        for px, py in [(x1, y1), (x2, y2)]:
            if 0 <= px < self.width and 0 <= py < self.height:
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = px + dx, py + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            self.vx[ny, nx] += self.linked_pair.vx / 12  # 8から12へ
                            self.vy[ny, nx] += self.linked_pair.vy / 12
    
    def propagate_fluid(self):
        """流体の拡散"""
        new_vx = np.copy(self.vx)
        new_vy = np.copy(self.vy)
        new_density = np.copy(self.density)
        
        for y in range(1, self.height - 1):
            for x in range(1, self.width - 1):
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
                    
                    current_vx = self.vx[y, x]
                    current_vy = self.vy[y, x]
                    speed = int(np.sqrt(current_vx**2 + current_vy**2))
                    
                    if speed > 0:
                        angle_index = int((np.arctan2(current_vy, current_vx) * 24 / (2 * np.pi)) % 24)
                    else:
                        angle_index = np.random.randint(0, 24)
                    
                    pisano_shift = (angle_index + self.step) % 24
                    dir_dx, dir_dy = PISANO_24_DIRS[pisano_shift]
                    
                    # 摩擦を減らす（流れが持続しやすく）
                    new_vx[y, x] = (current_vx * 7 + avg_vx * 3 + dir_dx / 10 - 0.5) / 10  # -1から-0.5へ
                    new_vy[y, x] = (current_vy * 7 + avg_vy * 3 + dir_dy / 10 - 0.5) / 10
                    new_density[y, x] = (self.density[y, x] * 7 + avg_d * 3) / 10
        
        self.vx = new_vx
        self.vy = new_vy
        self.density = new_density * 0.99  # 0.98から0.99へ（減衰を緩やかに）
        self.step += 1
    
    def step_simulation(self):
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
    print("温度設定: 7（高め）")
    print("異物質量: 8（軽量）")
    print("摩擦: 0.98（低め）")
    print("ゆらゆら漂い始めます...\n")
    
    sim = DriftingBrownian(width=80, height=40, temperature=7)
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    trajectory_x = []
    trajectory_y = []
    
    def update(frame):
        ax.clear()
        
        sim.step_simulation()
        
        cx, cy = sim.linked_pair.get_center()
        trajectory_x.append(cx)
        trajectory_y.append(cy)
        
        X, Y, U, V, D = sim.get_visualization_data()
        
        extent = [0, sim.width, 0, sim.height]
        
        # 密度を薄めに表示（漂う感を強調）
        im = ax.imshow(sim.density, extent=extent, origin='lower', 
                       cmap='hot', alpha=0.5, aspect='auto', vmin=0, vmax=5)
        
        # 速度ベクトル（流れを強調）
        speed = np.sqrt(U**2 + V**2)
        if np.max(speed) > 0.5:
            ax.quiver(X, Y, U, V, speed, cmap='cool', scale=400, width=0.003, alpha=0.6)
        
        # 繋がった2点（より目立つように）
        x1, y1 = sim.linked_pair.x1, sim.linked_pair.y1
        x2, y2 = sim.linked_pair.x2, sim.linked_pair.y2
        
        ax.plot([x1, x2], [y1, y2], 'w-', linewidth=4, alpha=0.9)
        ax.plot([x1, x2], [y1, y2], 'yo', markersize=10, markeredgecolor='orange', markeredgewidth=2.5)
        
        # 軌跡を長めに表示（漂いの軌跡）
        if len(trajectory_x) > 1:
            ax.plot(trajectory_x[-80:], trajectory_y[-80:], 'c-', linewidth=2, alpha=0.7)
            # 軌跡の先端を強調
            if len(trajectory_x) > 5:
                ax.plot(trajectory_x[-5:], trajectory_y[-5:], 'c-', linewidth=3, alpha=0.9)
        
        ax.set_title(f'Drifting Brownian Motion - Step {frame}', fontsize=14)
        ax.set_xlabel('X Position')
        ax.set_ylabel('Y Position')
        ax.set_xlim(0, sim.width)
        ax.set_ylim(0, sim.height)
        
        pair_speed = np.sqrt(sim.linked_pair.vx**2 + sim.linked_pair.vy**2)
        ax.text(5, sim.height - 5, 
                f'Speed: {pair_speed:.2f} | ω: {sim.linked_pair.angular_velocity:.3f} | Temp: {sim.temperature}', 
                color='white', fontsize=9, 
                bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        return ax,
    
    anim = animation.FuncAnimation(fig, update, frames=250, interval=70, blit=False)
    
    output_path = 'brownian_drifting_v3.gif'
    anim.save(output_path, writer='pillow', fps=14)
    print(f"\nアニメーション保存: {output_path}")
    
    plt.close()
    
    # 最終状態
    fig, ax = plt.subplots(figsize=(14, 7))
    
    X, Y, U, V, D = sim.get_visualization_data()
    extent = [0, sim.width, 0, sim.height]
    im = ax.imshow(sim.density, extent=extent, origin='lower', 
                   cmap='hot', alpha=0.5, aspect='auto')
    speed = np.sqrt(U**2 + V**2)
    ax.quiver(X, Y, U, V, speed, cmap='cool', scale=400, width=0.003, alpha=0.6)
    
    # 全軌跡を虹色グラデーションで表示
    points = np.array([trajectory_x, trajectory_y]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    
    from matplotlib.collections import LineCollection
    lc = LineCollection(segments, cmap='rainbow', linewidth=2.5, alpha=0.8)
    lc.set_array(np.linspace(0, 1, len(trajectory_x)))
    ax.add_collection(lc)
    
    x1, y1 = sim.linked_pair.x1, sim.linked_pair.y1
    x2, y2 = sim.linked_pair.x2, sim.linked_pair.y2
    ax.plot([x1, x2], [y1, y2], 'w-', linewidth=4)
    ax.plot([x1, x2], [y1, y2], 'yo', markersize=12, markeredgecolor='orange', markeredgewidth=3)
    
    ax.set_title(f'Full Drifting Trajectory (Step {sim.step})', fontsize=14)
    
    static_path = 'brownian_drifting_final.png'
    plt.savefig(static_path, dpi=150, bbox_inches='tight')
    print(f"最終状態保存: {static_path}")
    
    plt.close()
    
    print("\n=== Drifting Motion Complete ===")
    final_cx, final_cy = sim.linked_pair.get_center()
    print(f"総ステップ数: {sim.step}")
    print(f"最終位置: ({final_cx:.2f}, {final_cy:.2f})")
    print(f"移動距離: {np.sqrt((final_cx - sim.width/2)**2 + (final_cy - sim.height/2)**2):.2f}")
    print(f"軌跡の長さ: {len(trajectory_x)} ポイント")
    print("\nゆらゆら漂う異物の可視化完了")
