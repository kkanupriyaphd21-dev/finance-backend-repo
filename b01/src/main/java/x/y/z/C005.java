package x.y.z;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.math.BigDecimal;
import java.time.LocalDate;

@Entity
@Table(name = "entry_record")
@Getter
@Setter
@NoArgsConstructor
public class C005 {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    private String referenceCode;

    private BigDecimal amount;

    private BigDecimal rate;

    private LocalDate eventDate;
}
